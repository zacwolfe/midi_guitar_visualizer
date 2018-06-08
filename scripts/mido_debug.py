from mido import MidiFile
import mido
import sys

def shit(message):
    print("fukdik")

def play_midi(fname):
    mid = MidiFile(fname)
    # for i, track in enumerate(mid.tracks):
    #     print('Track {}: {}'.format(i, track.name))
    #     for msg in track:
    #         print(msg)

    port = mido.open_output(callback=shit)
    port.panic()

    print("the port",port)
    for msg in mid.play(meta_messages=True):
        if msg.type == 'lyrics':
            print(msg)
        port.send(msg)




if __name__ == '__main__':
    fname = '/Users/zacw/Documents/tmp/fella2.mid'

    if len(sys.argv) > 1:
        fname = sys.argv[1]

    mido.set_backend('mido.backends.rtmidi')
    play_midi(fname)