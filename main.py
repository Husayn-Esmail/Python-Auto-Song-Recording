# for recording audio
import sounddevice as sd
from scipy.io.wavfile import write
# for normalizing recordings
from pydub import AudioSegment, effects
# for identifying currently playing song
from ShazamAPI import Shazam
# for writing metadata to mp3
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
# for playing and pausing media
from pynput.keyboard import Key, Controller
# for arguments
import sys
# for identifying song in the background while recording the song
import multiprocessing
# for creating date based folders
import datetime
# for sleeping
import time
# for creating folders
import os
# for adding the option of running the program in single threaded mode
import SingleThreadedRecord
# trying to exit gracefully
import tkinter
from tkinter import ttk


# Global Constants ------------------------------
UNIDENTIFIED_INDEX = 0
INDEX_FILENAME = 'counter.txt'

"""
PyRecording usage:
pass in duration of song in minutes and seconds in the following format
3 56 = 3 minutes 56 seconds

the song will record, identify if possible, and then output as mp3
if the song cannot be identified then it will be labelled as
unidentified[index].mp3
"""


def get_song_length(minutes, seconds):
    """
    minutes: Str
    seconds: Str
    gets a song's length in seconds based on command line arguments
    returns total duration in seconds(float)
    """
    # convert minutes and seconds from strings to integers/float
    try:
        minutes = int(minutes)
    except Exception:
        print("Error, minutes is not an integer")
    
    try:
        seconds = float(seconds)
    except Exception:
        print("Error: seconds could not be converted to float")
    # convert minutes to seconds
    minutes *= 60
    total = minutes + seconds
    return total


def read_unidentified_index():
    """
    reads the index file and returns the value
    """
    index = 0   # initialize index
    try:
        f = open(INDEX_FILENAME, 'r')
        # read index and convert it to int
        index = int(f.readline())
        f.close()
    except Exception as e:
        print(e)
        # create new file and start index
        write_unidentified_index(index)
    return index
    

def write_unidentified_index(index):
    """
    Writes an index number to the index file.
    takes one argument: index (int)
    """
    try:
        f = open(INDEX_FILENAME, 'w')
        f.write(str(index))
        f.close()
    except Exception as e:
        print(e)
        print('error writing unidentified index')
        exit()

def get_unidentified_index():
    """ THIS FUNCTION MIGHT BE DEPRECATED
    if a song is unidentified this function will store
    the mp3 as unidentified[index].mp3 for manual revision later.
    This index comes from a file called counter.txt which is created
    if it does not exist and is read from and updated if it does exist.
    the counter should always be unique to prevent conflictsa and overwrites.
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

def identify_song(queue):
    """
    This function is meant to identify a song in the background in time to save the mp3 file
    """
    # recording paramaters
    sample_frequency = 44100
    duration = 10 # duration of recording in seconds -- increased from 5 to 10

    # recording of song
    recording = sd.rec(int(duration * sample_frequency), samplerate = sample_frequency, channels = 2)
    # wait for recording to finish
    sd.wait()
    # write out the sound bite
    write("Temps/identification.wav", sample_frequency, recording)

    audio_file_to_recognize = open("Temps/identification.wav", 'rb').read()
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
            queue.put_nowait(song_info)
            return
    except Exception as ex:
        print(ex)
    queue.put(song_info)


def recording(seconds, queue):
    """
    Records a song for the duration specified in seconds (integer)
    returns nothing
    """
    
    # recording paramaters
    # sampling freq
    sample_frequency = 96000
    duration = seconds

    # setup multi-process
    Q = multiprocessing.Queue()
    # setup process, no need for queue since no return
    prc = multiprocessing.Process(target=print_elapsed_time, args=(duration, Q))

    print("Starting Recording...")
    # start recording
    song_recording = sd.rec(int(duration * sample_frequency),
        samplerate = sample_frequency, channels = 2)

    # start the song
    play_pause()
    print("Recording in progress...")
    # start process
    prc.start()

    # wait for recording to finish
    sd.wait()
    # pause song and skip to next
    play_pause()
    skip_to_next()

    # wait for process to end
    prc.join()

    print("Writing recording to disk...")
    # write out the recording
    write("Temps/recording.wav", sample_frequency, song_recording)
    print("Finished Recording and writing to Temps/recording.wav")
    queue.put(None)

def normalize(filename, format):
    print("Normalizing Audio...")
    rawsound = AudioSegment.from_file(filename, format)  
    normalizedsound = effects.normalize(rawsound)  
    normalizedsound.export(filename, format=format)

def convert_to_mp3(song_info):
    print("Converting to mp3...")
    # normalize before conversion
    normalize("Temps/recording.wav", "wav")
    # converstion to mp3
    sound = AudioSegment.from_wav('Temps/recording.wav')
    title = song_info[0]
    artist = str(song_info[1])
    # Clean up song identification data
    title = title.replace('/', '-')
    artist = artist.replace('/', '-')

    # prepare to save the file
    date = datetime.date.today().isoformat()
    time = datetime.datetime.now()
    filename = f"Recordings/{date}/{title} - {artist}.mp3"

    if check_date_dir() != True:
        print(f"""{date} directory doesn't exist (likely due to day change)
Current Time: {time}
Creating {date} directory""")
        # actually making the directory
        os.mkdir(f"Recordings/{date}")

    # save the file
    sound.export(filename, format='mp3', bitrate="320k")
    song = filename
    mp3file = MP3(song, ID3=EasyID3)
    mp3file['title'] = [title]
    mp3file['artist'] = [artist]
    print("Saving...")
    mp3file.save()
    print("Saved")

def play_pause():
    """
    automates pressing the play/pause media key when recording.
    """
    print("Play/Pause")
    keyboard = Controller()
    keyboard.press(Key.media_play_pause)
    keyboard.release(Key.media_play_pause)

def print_elapsed_time(total_time, Q):
    """
    Prints the time elapsed out of a given total, total_time (float in seconds).
    Meant to help give real time status of the recording.
    """
    current_time = 0
    minutes = total_time // 60 # integer divison by seconds
    seconds = total_time - (minutes * 60) # subtract minutes in form of seconds

    print(">>> Total time calculated: %d:%02d" % (minutes, seconds))
    while current_time <= total_time:
        print(">>> Elapsed Time in seconds: %d/%02d"% (current_time, total_time), flush=True, end="\r")
        time.sleep(1) # sleep for one second to reflect elapsed time
        current_time += 1
    # print the empty line so the next print statement doesn't overwrite.
    print('')

def multi_process(record_duration):
    """
    Sets up everything for running parallel processes for recording
    and idenitifying the song. It's basically the main userside recording function.
    Requires the record duration in seconds.
    Returns the song's info (title and artist) in a tuple.
    """
    print("Setting up multi_process...")
    # create Queue to get return values
    Q = multiprocessing.Queue()
    print("Queue init'd...")
    # creating processes for each of the functions
    prc1 = multiprocessing.Process(target=recording, args=(record_duration,Q))
    prc2 = multiprocessing.Process(target=identify_song, args=(Q,))
    rets = []
    # starting the first process
    prc1.start()
    # start second process
    prc2.start()
    print("Processes started")

    rets.append(Q.get())
    rets.append(Q.get())
    # wait until first process is done
    prc1.join()
    # wait until second process is done
    prc2.join()
    # when both processes are finished
    print("Processes complete!")
    return rets[0] # only return the first value cuz that's the meta data

def record_song(minutes, seconds):
    # calculate song length 
    song_length = get_song_length(minutes, seconds)

    # start the recording process
    song_info = multi_process(song_length)

    # check if song was identified.
    if song_info != None:
        convert_to_mp3(song_info)
    else:
        global UNIDENTIFIED_INDEX # required to access global variable
        song_info = ("unidentified", UNIDENTIFIED_INDEX)
        UNIDENTIFIED_INDEX += 1 # increment unidentified index
        convert_to_mp3(song_info)
        # write the unidentified index back to the file
        write_unidentified_index(UNIDENTIFIED_INDEX)
    return song_info

def makedirs():
    # list the contents of the current directory
    dir = os.listdir()
    # if recordings doens't exist, create the directory
    if "Recordings" not in dir:
        print("making directory to hold recordings")
        os.mkdir("Recordings")
    else:
        print("Recordings directory exists")

    # if temps not in dir
    if "Temps" not in dir:
        print("making directory for temporary files")
        os.mkdir("Temps")
    else:
        print("Temps directory exists")
    
    # Ensure directory for current date exists.
    date = datetime.date.today().isoformat()
    if check_date_dir() == False:
        print(f"making directory {date}")
        os.mkdir(f"Recordings/{date}")
    else:
        print(f"directory {date} already exists")

def check_date_dir():
    """
    Checks if the current date directory exists or not.
    """
    date = datetime.date.today().isoformat()
    if date not in os.listdir("Recordings"):
        return 0
    return 1


def set_interrupt(interrupt_var):
    """
    bad programming, this changes the variable inside the function
    """
    interrupt_var = 1
    print(interrupt_var)
    print("set_interrupt called")

def wind_func(int_var):
    tk = tkinter.Tk()
    tk.title("PyRecording")

    frame = ttk.Frame(tk, padding=10)
    frame.grid()
    label_text = "Pause exits the program after the current song finishes"
#    label_text = "Exit stops the program immediately, pause exits after the next song ends"
    ttk.Label(frame, text=label_text).grid(column=0, row=0)
    ttk.Button(frame, text="Pause", command=lambda: set_interrupt(int_var)).grid(column=0, row=1)
    # ttk.Button(frame, text="Exit", command=tk.destroy).grid(column=0, row=2)
    tk.mainloop()


def batch(filename):
    print("Running in batch mode...")
    song_lengths = []
    with open(filename, "r") as f:
        # split by spaces
        for line in f:
            song_lengths.append(line.split())

    # ensure lengths were entered
    if song_lengths == []:
        raise Exception("Error, no lengths in file")
    
    # read the undentified index regardless before starting the record loop
    UNIDENTIFIED_INDEX = read_unidentified_index()

    # make dirs
    makedirs()
    print ("*" * 20)
    interrupt_status = 0
    prc = multiprocessing.Process(target=wind_func, args=[interrupt_status])
    prc.start()
    
    # convert all entries to int
    for array in song_lengths:
        minutes = int(array[0])
        seconds = float(array[1])
        info = record_song(minutes, seconds)
        print(f"Recorded \"{info[0]} - {info[1]}.mp3\"")
        print("*" * 20)
        
        print("interrupt_status")
        if interrupt_status:
               print("Interrupt Called")
               break

    prc.join()

def skip_to_next():
    print("skipping to next...")
    keyboard = Controller()
    keyboard.press(Key.media_next)
    keyboard.release(Key.media_next)

if __name__ == '__main__':
    HELP = """
        USAGE:
        python3 main.py -f [filename] -- see readme for formatting information
        python3 main.py [minutes] [seconds]
        python3 main.py -sf [filename] # runs the program in single threaded mode on a batch of songs
        python3 main.py -s [minutes] [seconds] # runs the program in single threaded mode on a single song
        i.e. python3 main.py 5 43 would be 5 minutes 43 seconds duration of song
        python3 main.py -- shows this help screen
        """
    # deal with commandline arguments
    n = len(sys.argv)

    # read the index before everything else.
    UNIDENTIFIED_INDEX = read_unidentified_index()

    # batch argument
    if n == 2:
        if sys.argv[1] == '-f' or sys.argv[1] == '-sf':
            print("You'll need to enter a filename")
            f = input("enter a filename: ")
            if f != "" and sys.argv[1] == '-f':
                batch(f)
            elif f != "" and sys.argv[1] == '-sf':
                SingleThreadedRecord.single_threaded_batch(f)
        else:
            print("Error invalid argument")
            print(HELP)
            sys.exit()
    elif n == 3:
        # handle case where filename is being passed
        if sys.argv[1] == '-f':
            filename = sys.argv[2]
            batch(filename)
        elif sys.argv[1] == '-sf':
            filename = sys.argv[2]
            SingleThreadedRecord.single_threaded_batch(filename)
        elif sys.argv[1] == '-c':
            filename = sys.argv[2]
            # identify song
            song_info = SingleThreadedRecord.single_threaded_identify_song(filename)
            if song_info != None:
                convert_to_mp3(song_info)
            else:
                song_info = ("unidentified", UNIDENTIFIED_INDEX)
                UNIDENTIFIED_INDEX += 1 # increment unidentified index
                convert_to_mp3(song_info)
                # write the index back to the file
                write_unidentified_index(UNIDENTIFIED_INDEX)
        else:
            minutes = sys.argv[1]
            seconds = sys.argv[2]
            # handle weird input combination
            try:
                verify_minutes = int(minutes)
                verify_seconds = float(seconds)
            except (ValueError) as exc:
                print("Error, either minutes was not an integer or seconds could not be converted to float")
                sys.exit()

            # record song
            makedirs()
            record_song(minutes, seconds)

    elif n == 4:
        if sys.argv[1] == '-s':
            minutes = sys.argv[2]
            seconds = sys.argv[3]
            # handle weird input combination
            try:
                verify_minutes = int(minutes)
                verify_seconds = float(seconds)
            except (ValueError) as e:
                print("Error, either minutes was not an integer or seconds could not be converted to float")
                sys.exit()
            makedirs()
            # record song in single threaded mode
            SingleThreadedRecord.single_thread_record_song(minutes, seconds)

    # if no argument has been given, show the help screen
    else:
        print(HELP)
