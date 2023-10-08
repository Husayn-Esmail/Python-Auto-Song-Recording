from ShazamAPI import Shazam
import sys

if __name__ == '__main__':
    filename = sys.argv[1]
    song_to_recognize = open(filename, "rb").read()
    shazam = Shazam(song_to_recognize)
    recognize_generator = shazam.recognizeSong()
    song_info = None
    info = next(recognize_generator)
    track_info = info[1]
    if 'track' in track_info:
        title = track_info['track']['title']
        artist = track_info['track']['subtitle']
        print(title)
        print(artist)