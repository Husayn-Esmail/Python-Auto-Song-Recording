# PyRecording

Software to record music from apple music, identify the song and save the recording

***NOTE***: This program requires you have an audio interface that supports loopback recording and an Apple Music Subscription
You must also ensure that your default input is specified as the audio interface before starting the recording

## Compatiblity

Mac only at the moment

## USAGE

Since the program doesn't know how long the song is before recording, you need to give it the length of your song you want to record
this can be done in the following way.
"""
python3 main.py [minutes] [seconds]
python3 batch_record.py
"""
enter the name of a .txt file containing entries on each line in the form,
[minutes] [seconds]
[minutes] [seconds]

After that all you have to do is wait. The program will record the song, identify it, write tags and save the recording.

future changes:
save recordings to a specific folder
clean up temporary files after the job is done like identification.wav and recording.wav
allow batch recordings by allowing a specified batch time file to allow playlists to just be run and recorded overnight
figure out how to deal with songs that can't be identified in a better manner (perhaps pulling from the apple music api
instead of using shazam to id songs)
