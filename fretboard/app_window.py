from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.config import Config
from .fretboard import Fretboard
from .tunings import P4Tuning



class AppWindow(RelativeLayout):

    height_ratio = .36
    initial_width = 1800
    initial_screen_loc_x = 50
    initial_screen_loc_y = 400

    def __init__(self, midi_config, **kwargs):
        super(AppWindow, self).__init__(**kwargs)
        self.midi_config = midi_config

        with self.canvas:
            Window.size = (self.initial_width, self.initial_width * self.height_ratio)
            Window.left = self.initial_screen_loc_x
            Window.top = self.initial_screen_loc_y
            Window.clearcolor = (1, 1, 1, 1)
            tuning = P4Tuning()
            self.rect = Rectangle(pos=self.pos, size=self.size, group='fb')
            self.fretboard = Fretboard(tuning=tuning, pos_hint={'x':0, 'y':0}, size_hint=(1, 0.5))
            self.add_widget(self.fretboard)


        with self.canvas.before:
            pass

        with self.canvas.after:
            pass

        self.bind(size=self.size_changed)
        self.midi_config.open_input(self.midi_message_received)

    def size_changed(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def start_listening_midi(self):
        self.midi_config.open_input()

    def midi_message_received(self, midi_note, channel, on):
        # print('midi!!! {}'.format(message))
        if on:
            self.fretboard.midi_note_on(midi_note, channel)
        else:
            self.fretboard.midi_note_off(midi_note, channel)


