import mido
import collections

def get_midi_ports():
    return mido.get_input_names()

def get_midi_defaults():
    return {
        'midi_port': '',
    }

class Midi(object):
    # default_port = 'Fishman TriplePlay TP Control'
    # default_port = 'Fishman TriplePlay TP Guitar'

    def __init__(self, note_filter, default_port, midi_callback):
        self.note_filter = note_filter
        self.default_port = default_port
        self.midi_callback = midi_callback

    def open_input(self):
        self.input_port = mido.open_input(name=self.default_port, callback=self.midi_message_received)
        if self.input_port.closed:
            self.input_port = mido.open_input(callback=self.midi_message_received)
        print("we got port {}".format(self.input_port))


    def midi_message_received(self, message):
        if message.type not in ['note_on', 'note_off']:
            return

        if not self.note_filter.filter_note(message):
            print('skipping {}'.format(message))
            return

        self.midi_callback(message.note, message.channel, message.type == 'note_on')

    def shutdown(self):
        if self.input_port:
            self.input_port.close()

    def set_default_port(self, port, open_port=False):
        self.shutdown()
        self.default_port = port
        if open_port:
            self.open_input()


class NoteFilter(object):
    note_queue = collections.deque(maxlen=4)

    def filter_note(self, message):

        self.note_queue.append(message)
        return message