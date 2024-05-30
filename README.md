# PyRecording

Software to record music from apple music or other streaming softwares, identify the song, and save the
recording. 

**_NOTE_**: This program was written for educational purposes only. Respect all laws and regulations in
your region. I will not be held responsible if you get into trouble with the law. Artists work hard to
create music and we should all respect that work.
This program requires you have an audio interface that supports loopback recording and an music streaming 
subscription. You must also ensure that your default input is specified as the audio interface before 
starting the recording. You also need to install ffmpeg for the program to work properly.
On Mac I recommend using brew.
Also the successrate of this program is heavily dependent on the input provided. I've had anywhere from
10% of successful recordings to 100% of successful recordings with an average of about 50% success. This
is because the method for determining song length is manual and inconsistent. The programs which play music
lie to you. They sometimes end earlier or later and you can never know.

## Setup

### Mac OS

Install ffmpeg

```Bash
brew install ffmpeg
```

clone the repository and install dependencies

```Bash
git clone https://github.com/Husayn-Esmail/Python-Auto-Song-Recording.git
cd Python-Auto-Song-Recording
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Compatiblity

Mac (only been tested on this, it could work on windows I just don't know)

## Usage

Since the program doesn't know how long the song is before recording, you
need to give it the length of your song you want to record this can be
done in the following way.

```Bash
python3 main.py [minutes] [seconds]
python3 main.py -s [minutes] [seconds]
python3 main.py -f [filename]
python3 main.py -sf [filename]
python3 main.py # shows help
```

**NOTE** that if you don't enter a filename, you'll be asked to input a
filename when running main.py

enter the name of a .txt file containing entries on each line in the form:
[minutes] [seconds]
[minutes] [seconds]


**Pro Tip**: The program ignores everything after minutes and seconds so if you're doing a lot of songs
it can be very helpful to comment the names of each songs after the length, for example:

3 07    # We Don't Talk Anymore

Naturally, I don't use the full name, usually just the first two words or something because I'm the only
one who needs to know what song it is.

After that all you have to do is wait. The program will record the song,
identify it, write tags, and save the recording.

## Future changes

- ~~clean up temporary files after the job is done like identification.wav and recording.wav (Kept these for debugging)~~
- figure out how to deal with songs that can't be identified in a better manner (perhaps
pulling from the apple music api instead of using shazam to id songs)
- ~~indication for when identification is happening~~
- ~~improve performance~~
- ~~listen for a keyboard command or combination to exit cleanly if user wants to stop the job early or on the next end of song for checkpointing~~
- ~~fix program so that it doesn't break at midnight~~
- ~~There's a bug when keeping track of the unidentified tracks where if the program crashes, the counter.txt file is not updated.~~
- Support reading certain parameters from a configuration file (while giving defaults)
- ~~add support for a debug flag~~
