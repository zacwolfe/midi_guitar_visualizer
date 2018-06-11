from mido import MidiFile
import mido
import sys


def play_midi(fname):
    mid = MidiFile(fname)
    # for i, track in enumerate(mid.tracks):
    #     print('Track {}: {}'.format(i, track.name))
    #     for msg in track:
    #         print(msg)

    port = mido.open_output()

    print("the port",port)
    for msg in mid.play():
        port.send(msg)







if __name__ == '__main__':
    fname = '/Users/zacw/Documents/mma_songs/mma-songs-16.06/triste.mid'

    if len(sys.argv) > 1:
        fname = sys.argv[1]

    # mido.set_backend('mido.backends.rtmidi')
    play_midi(fname)