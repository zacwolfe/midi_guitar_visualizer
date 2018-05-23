from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ConfigParserProperty
from .fretboard import Fretboard
from .tunings import P4Tuning
from .midi import Midi, NoteFilter
from scales.scales import Scales, Chords
from kivy.config import ConfigParser

class AppWindow(RelativeLayout):

    height_ratio = ConfigParserProperty(0.0, 'window', 'height_ratio', 'app', val_type=float)
    initial_width = ConfigParserProperty(0, 'window', 'initial_width', 'app', val_type=int)
    initial_screen_loc_x = ConfigParserProperty(0, 'window', 'initial_screen_loc_x', 'app', val_type=int)
    initial_screen_loc_y = ConfigParserProperty(0, 'window', 'initial_screen_loc_y', 'app', val_type=int)
    midi_port = ConfigParserProperty(0, 'midi', 'midi_port', 'app')


    def __init__(self, **kwargs):
        super(AppWindow, self).__init__(**kwargs)

        self.tuning = P4Tuning(int(ConfigParser.get_configparser('app').get('fretboard','num_frets')))
        self.note_filter = NoteFilter(self.tuning)
        if self.midi_port:
            self.midi_config = Midi(self.note_filter, self.midi_port, self.midi_message_received)

        self.scale_config = Scales()
        self.chords_config = Chords()

        with self.canvas:
            Window.size = (self.initial_width, self.initial_width * self.height_ratio)
            Window.left = self.initial_screen_loc_x
            Window.top = self.initial_screen_loc_y
            Window.clearcolor = (1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, group='fb')
            self.fretboard = Fretboard(tuning=self.tuning, scale_config=self.scale_config, chord_config=self.chords_config, pos_hint={'x':0, 'y':0}, size_hint=(1, 0.5))
            self.add_widget(self.fretboard)




        with self.canvas.before:
            pass

        with self.canvas.after:
            pass

        self.bind(size=self.size_changed)

        # self.init_midi()


    def size_changed(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def init_midi(self):
        self.midi_config.open_input()

    def reload_midi(self):
        self.midi_config.set_default_port(self.midi_port, open_port=True)

    def reload_scales(self):
        self.scale_config.load_scales()


    def midi_message_received(self, midi_note, channel, on):
        # print('midi!!! {}'.format(message))
        if on:
            self.fretboard.midi_note_on(midi_note, channel)
        else:
            self.fretboard.midi_note_off(midi_note, channel)


