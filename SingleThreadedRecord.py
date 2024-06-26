# audio recording
import sounddevice as sd
from scipy.io.wavfile import write
# for identfiying currently playing song
from ShazamAPI import Shazam
# import functions from main that will work here
from main import get_song_length, \
    read_unidentified_index, \
    write_unidentified_index, \
    makedirs, \
    play_pause, convert_to_mp3, \
    UNIDENTIFIED_INDEX, INDEX_FILENAME


def single_threaded_identify_song(filename):
    """
    Note that you must call makedirs before calling this function
    """
    print(f"identifying {filename}...")
    audio_file_to_recognize = open(filename, "rb").read()
    shazam = Shazam(audio_file_to_recognize)
    recognize_generator = shazam.recognizeSong()
    song_info = None
    try:
        info = next(recognize_generator)
        track_info = info[1]
        if 'track' in track_info:
            title = track_info['track']['title']
            artist = track_info['track']['subtitle']
            song_info = (title, artist)
    except Exception as e:
        print(e)
    if song_info != None:
        print(f"identified artist: {song_info[1]} song: {song_info[0]}")
    else:
        print("Song unidentifiable.")
    return song_info

def single_threaded_recording(seconds):
    sample_frequency = 96000
    duration = seconds
    sample_freq_by_duration = int(duration * sample_frequency)

    # record song
    song_recording = sd.rec(sample_freq_by_duration, samplerate=sample_frequency, channels=2)

    # play song
    play_pause()

    # wait for recording to finish
    sd.wait()

    # pause song
    play_pause()

    # write out the recording
    print('Writing recording to disk...')
    write("Temps/recording.wav", sample_frequency, song_recording)


def single_thread_record_song(minutes, seconds):
    global UNIDENTIFIED_INDEX
    print("Running single threaded record song...")
    # calculate song length
    song_length = get_song_length(minutes, seconds)
    print(f"Song length calculated: {song_length}")
    print("recording")
    single_threaded_recording(song_length)
    song_info = single_threaded_identify_song("Temps/recording.wav")
    if song_info != None:
        convert_to_mp3(song_info)
    else:
        song_info = ("unidentified", UNIDENTIFIED_INDEX)
        UNIDENTIFIED_INDEX += 1
        convert_to_mp3(song_info)
        # write unidentified index to prevent dataloss
        write_unidentified_index(UNIDENTIFIED_INDEX)
    return song_info

def single_threaded_batch(filename):
    print("Running in single-threaded batch mode...")
    song_lengths = []
    with open(filename, "r") as f:
        # split by spaces
        for line in f:
            song_lengths.append(line.split())

        # ensure lengths were entered
        if song_lengths == []:
            raise Exception("Error, no lengths in file")

        # read the unidentified index before starting the record loop
        UNIDENTIFIED_INDEX = read_unidentified_index()
        # make directories
        makedirs()

        # convert all entries to int
        for array in song_lengths:
            minutes = int(array[0])
            seconds = float(array[1])
            info = single_thread_record_song(minutes, seconds)
            print(f"Recorded \"{info[0]} - {info[1]}.mp3\"")