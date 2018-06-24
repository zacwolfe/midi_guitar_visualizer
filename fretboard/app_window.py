from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ConfigParserProperty
from .fretboard import Fretboard
from .tunings import P4Tuning
from .midi import Midi, NoteFilter
from .pattern_mapper import P4TuningPatternMatcher, StandardTuningPatternMatcher
from .player_panel import PlayerPanel
from scales.scales import Scales, Chords, Patterns
from kivy.config import ConfigParser
from kivy.uix.boxlayout import BoxLayout
class AppWindow(BoxLayout):

    height_ratio = ConfigParserProperty(0.0, 'window', 'height_ratio', 'app', val_type=float)
    initial_width = ConfigParserProperty(0, 'window', 'initial_width', 'app', val_type=int)
    initial_screen_loc_x = ConfigParserProperty(0, 'window', 'initial_screen_loc_x', 'app', val_type=int)
    initial_screen_loc_y = ConfigParserProperty(0, 'window', 'initial_screen_loc_y', 'app', val_type=int)
    midi_port = ConfigParserProperty(0, 'midi', 'midi_port', 'app')
    midi_output_port = ConfigParserProperty(0, 'midi', 'midi_output_port', 'app')


    def __init__(self, midi_player, **kwargs):
        super(AppWindow, self).__init__(**kwargs)
        self.midi_player = midi_player
        self.orientation='vertical'
        self.tuning = P4Tuning(int(ConfigParser.get_configparser('app').get('fretboard','num_frets')))
        self.note_filter = NoteFilter(self.tuning)
        if self.midi_port:
            self.midi_config = Midi(self.midi_player, self.note_filter, self.midi_port, self.midi_message_received, self.midi_output_port)

        self.scale_config = Scales()
        self.chords_config = Chords()
        self.patterns_config = Patterns()

        with self.canvas:
            Window.size = (self.initial_width, self.initial_width * self.height_ratio)
            Window.left = self.initial_screen_loc_x
            Window.top = self.initial_screen_loc_y
            Window.clearcolor = (1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, group='fb')

        pattern_mapper = P4TuningPatternMatcher(self.tuning, self.chords_config, self.scale_config, self.patterns_config)
        self.fretboard = Fretboard(tuning=self.tuning, pattern_mapper=pattern_mapper, pos_hint={'x':0, 'y':0}, size_hint=(1, 0.3))

        self.player_panel = PlayerPanel(fretboard=self.fretboard, midi_config=self.midi_config, size_hint=(1, 0.7))
        self.add_widget(self.player_panel)
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
        self.midi_config.open_output()

    def reload_midi(self):
        self.midi_config.set_default_input_port(self.midi_port, open_port=True)
        self.midi_config.set_default_output_port(self.midi_output_port, open_port=True)

    def shutdown_midi(self):
        if self.midi_player:
            self.midi_player.stop()

        if self.midi_config:
            self.midi_config.shutdown()
    def reload_scales(self):
        self.scale_config.load_scales()


    def midi_message_received(self, midi_note, channel, on, time=None):
        # print('midi!!! {}'.format(message))
        if on:
            self.fretboard.midi_note_on(midi_note, channel, time)
            # if self.midi_config:
                # last_notes = self.midi_config.note_filter.get_note_queue()
                # if last_notes:
                #     pass
                    # self.fretboard.show_pattern()
        else:
            self.fretboard.midi_note_off(midi_note, channel)


