import mido
import collections

class Midi(object):
    # default_port = 'Fishman TriplePlay TP Control'
    # default_port = 'Fishman TriplePlay TP Guitar'

    def __init__(self, note_filter, default_port):
        self.note_filter = note_filter
        self.default_port = default_port

    def open_input(self, callback):
        self.midi_callback = callback
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



class NoteFilter(object):
    note_queue = collections.deque(maxlen=4)

    def filter_note(self, message):

        self.note_queue.append(message)
        return message