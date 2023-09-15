from ShazamAPI import Shazam

if __name__ == '__main__':
    song_to_recognize = open("Recordings/2023-08-01/I Don't Miss You - JP Saxe.mp3", "rb").read()
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