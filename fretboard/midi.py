import mido
import collections
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.app import App
from constants import current_time_millis

def get_midi_ports():
    return mido.get_input_names()

def get_midi_defaults():
    return {
        'midi_port': '',
    }



class Midi(object):

    input_port = ''

    def __init__(self, note_filter, default_port, midi_callback):
        self.note_filter = note_filter
        self.default_port = default_port
        self.midi_callback = midi_callback

    def open_input(self):
        try:
            self.input_port = mido.open_input(name=self.default_port, callback=self.midi_message_received)
        except IOError:
            print("i'm rebitching")
            box = BoxLayout(orientation="vertical")

            label = Label(text='Could not load midi port {}. \nPlease select a valid midi port'.format(self.default_port))
            box.add_widget(label)
            button_select = Button(text='OK', size_hint=(.3, .2))
            box.add_widget(Widget(size_hint=(None, .02)))
            box.add_widget(button_select)

            popup = Popup(title='Midi Port Not Found', content=box, size_hint=(None, None), size=(1000, 400))

            def dismiss():
                popup.dismiss()
                App.get_running_app().open_settings()

            button_select.bind(on_release=lambda *args: dismiss())
            popup.open()



    def midi_message_received(self, message):
        if message.type not in ['note_on', 'note_off']:
            return

        if not self.note_filter.filter_note(message):
            # print('skipping {}'.format(message))
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
    min_velocity = 20
    open_string_min_velocity = 50
    max_fret_distance = 6
    max_seq_gap_millis = 250
    skip_open_strings = True

    def __init__(self, tuning):
        self.tuning = tuning

    def filter_note(self, message):
        # print("got message {}".format(message))

        now = current_time_millis()
        message.time = now
        if message.type == 'note_on':
            if (self.tuning.is_impossible_note(message.channel, message.note)):
                return
            if (self.tuning.is_open_string(message.channel, message.note) and (self.skip_open_strings or message.velocity < self.open_string_min_velocity)):
                return
            elif message.velocity < self.min_velocity:
                return
            else:
                if len(self.note_queue) > 0:
                    last_msg = self.note_queue[-1]
                    # print("the time diff is {} and dist {}".format(
                    #     now - last_msg.time,
                    #     self.tuning.get_distance(last_msg.channel, last_msg.note, message.channel, message.note)
                    # ))
                    if now - last_msg.time < self.max_seq_gap_millis and \
                            self.tuning.get_distance(last_msg.channel, last_msg.note, message.channel, message.note) > self.max_fret_distance:
                        print("skipping this dick cuz its wide...",  self.tuning.get_distance(last_msg.channel, last_msg.note, message.channel, message.note), now - last_msg.time)
                        return

            # if self.tuning.is_open_string(message.channel, message.note):
            #     print("got open string {}".format(message))

            self.note_queue.append(message)

        return message