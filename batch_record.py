from main import record_song
def batch(filename):
    song_lengths = []
    with open(filename, "r") as f:
        # split by spaces
        for line in f:
            song_lengths.append(line.split())

    # ensure lengths were entered
    if song_lengths == []:
        raise Exception("Error, no lengths in file")
    
    # convert all entries to int
    for array in song_lengths:
        minutes = int(array[0])
        seconds = int(array[1])
        record_song(minutes, seconds)

if __name__ == '__main__':
    f = input("enter a filename: ")
    batch(f)
