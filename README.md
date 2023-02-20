# PyRecording

Software to record music from apple music, identify the song and save the
recording

***NOTE***: This program requires you have an audio interface that supports
loopback recording and an Apple Music Subscription
You must also ensure that your default input is specified as the audio
interface before starting the recording

## Compatiblity

Mac (only been tested on this, it could work on windows I just don't know)

## Usage

Since the program doesn't know how long the song is before recording, you
need to give it the length of your song you want to record this can be
done in the following way.

``` Bash
python3 main.py [minutes] [seconds]
python3 main.py -f [filename]
python3 main.py # shows help
```

**NOTE** that if you don't enter a filename, you'll be asked to input a
filename when running main.py

enter the name of a .txt file containing entries on each line in the form:
[minutes] [seconds]
[minutes] [seconds]

After that all you have to do is wait. The program will record the song,
identify it, write tags and save the recording.

## Future changes

clean up temporary files after the job is done like identification.wav and recording.wav
figure out how to deal with songs that can't be identified in a better manner (perhaps
pulling from the apple music api instead of using shazam to id songs)
