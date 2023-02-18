# import library
# for recording audio
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
# probably for deleting intermediary files
import os
# for recording
from pydub import AudioSegment
# for identifying currently playing song
from ShazamAPI import Shazam
# for printing pretty json
import json
# for writing metadata to mp3
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
# for automatically playing and pausing media
from pynput.keyboard import Key, Controller
# for arguments
import sys

# for identifying song in the background while recording the song
import multiprocessing


# Global Constants
INDEX_FILENAME = 'counter.txt'


"""
PyRecording usage:
pass in duration of song in minutes and seconds in the following format
3 56 = 3 minutes 56 seconds

the song will record, identify if possible, and then output as mp3
if the song cannot be identified then it will be labelled as
unidentified[index].mp3
"""

# works
def get_song_length(minutes, seconds):
    """
    minutes: Str
    seconds: Str
    gets a song's length in seconds based on command line arguments
    returns total duration in seconds(int)
    """
    # convert minutes and seconds from strings to integers
    try:
        minutes = int(minutes)
    except Exception:
        print("Error, minutes is not an integer")
    
    try:
        seconds = int(seconds)
    except Exception:
        print("Error: seconds is not an integer")
    # convert minutes to seconds
    minutes *= 60
    total = minutes + seconds
    return total


# doesn't work
def get_unidentified_index():
    """
    if a song is unidentified this function will store
    the mp3 as unidentified[index].mp3 for manual revision later
    this index comes from a file called counter.txt which is created
    if it does not exist and is read from and updated if it does exist
    the counter should always be unique to prevent conflicts
    """
    try: 
        # open index file to get unique index
        file_object = open(INDEX_FILENAME, 'r')
        content = file_object.readline()
        print(content)
        # close file
        file_object.close()
        int_content = int(content)
        # increment counter
        int_content += 1
        print(int_content)
        # write back into index file
        file_object = open(INDEX_FILENAME, 'w')
        str_content = str(int_content)
        file_object.write(str_content)
        # # close file 
        file_object.close()
    except Exception as ex:
        print(ex)
        # create new file and start index
        file_object = open(INDEX_FILENAME, 'w')
        content = "0"
        int_content = 0
        file_object.write(content)
        # close file
        file_object.close()
    return int_content


# works
def identify_song(queue):
    """
    This function is meant to identify a song in the background in time to save the mp3 file
    """
    # recording paramaters
    sample_frequency = 44100
    duration = 5 # duration of recording in seconds

    # recording of song
    recording = sd.rec(int(duration * sample_frequency), samplerate = sample_frequency, channels = 2)
    # wait for recording to finish
    sd.wait()
    # write out the sound bite
    write("identification.wav", sample_frequency, recording)

    audio_file_to_recognize = open("identification.wav", 'rb').read()
    shazam = Shazam(audio_file_to_recognize)
    recognize_generator = shazam.recognizeSong()
    song_info = None
    try:
        while True:
            info = next(recognize_generator)
            track_info = info[1]
            if 'track' in track_info:
                title = track_info['track']['title']
                artist = track_info['track']['subtitle']
                song_info = (title, artist)
                queue.put_nowait(song_info)
                return
    except Exception as ex:
        print(ex)
    queue.put(song_info)

# works
def recording(seconds, queue):
    """
    Records a song for the duration specified in seconds (integer)
    returns nothing
    """
    # play the song
    play_pause()
    # recording paramaters
    # sampling freq
    sample_frequency = 48000
    duration = seconds
    # recording of the song
    recording = sd.rec(int(duration * sample_frequency),
        samplerate = sample_frequency, channels = 2)
    # wait for recording to finish
    sd.wait()
    # pause song
    play_pause()
    # write out the recording
    write("recording.wav", sample_frequency, recording)
    queue.put(None)

# works
def convert_to_mp3(song_info):
    # converstion to mp3
    sound = AudioSegment.from_wav('recording.wav')
    title = song_info[0]
    artist = song_info[1]
    filename = '%s - %s.mp3' % (title, artist)
    sound.export(filename, format='mp3')
    song = filename
    mp3file = MP3(song, ID3=EasyID3)
    mp3file['title'] = [title]
    mp3file['artist'] = [artist]
    mp3file.save()

# works
def play_pause():
    """
    automates pressing the play/pause media key when recording.
    """
    keyboard = Controller()
    keyboard.press(Key.media_play_pause)
    keyboard.release(Key.media_play_pause)


# unknown
def multi_process(record_duration):
    # create Queue to get return values
    Q = multiprocessing.Queue()
    # creating processes for each of the functions
    prc1 = multiprocessing.Process(target=recording, args=(record_duration,Q))
    prc2 = multiprocessing.Process(target=identify_song, args=(Q,))
    rets = []
    # starting the first process
    prc1.start()
    # start second process
    prc2.start()

    rets.append(Q.get())
    rets.append(Q.get())
    # wait until first process is done
    prc1.join()
    # wait until second process is done
    prc2.join()
    # when both processes are finished
    print("complete")
    return rets[0] # only return the first value cuz that's the meta data

def record_song(minutes, seconds):
    # calculate song length 
    song_length = get_song_length(minutes, seconds)
    # give 2 seconds buffer time for recording
    # song_length += 2
    song_info = multi_process(song_length)
    if song_info != None:
        convert_to_mp3(song_info)
    else:
        unidentified_index = get_unidentified_index()
        song_info = ("unidentified", unidentified_index)
        convert_to_mp3(song_info)

if __name__ == '__main__':
    # argument checking
    n = len(sys.argv)
    if n != 3:
        raise Exception("Error: need minutes and seconds.")
        
    # extract the arguments
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    # calculate song length 
    song_length = get_song_length(arg1, arg2)
    # give 2 seconds buffer time for recording
    # song_length += 2
    song_info = multi_process(song_length)
    if song_info != None:
        convert_to_mp3(song_info)
    else:
        unidentified_index = get_unidentified_index()
        song_info = ("unidentified", unidentified_index)
        convert_to_mp3(song_info)

