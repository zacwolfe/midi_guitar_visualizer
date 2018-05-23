import toml
from kivy.config import ConfigParser
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.app import App
import re

scale_systems_file = 'scale_systems.toml'

class Scales(object):

    # scales_file = ConfigParserProperty(scale_systems_file, 'harmonic_definitions', 'scale_system_file', 'app', val_type=str)

    def __init__(self, **kwargs):
        super(Scales, self).__init__(**kwargs)
        self.load_scales()

    def load_scales(self):
        scales_file = ConfigParser.get_configparser('app').get('harmonic_definitions', 'scale_system_file')
        try:

            # ConfigParser.get_configparser('app').get('fretboard', key)
            print("das goddam scales file is {}".format(scales_file))
            scale_systems = toml.load(scales_file)

            systems = scale_systems.get('systems')
            self.scales = {**scale_systems.get('scales'), **systems}

            for s in self.scales.values():
                s.sort()

        except IOError:
            box = BoxLayout(orientation="vertical")

            label = Label(
                text='Could not load scales file {}. \nPlease select a valid scales file'.format(scales_file))
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

    def get_scale(self, name):
        return self.scales.get(name)


def lookahead(chord, index):
    if index < 0 or index + 1 >= len(chord):
        return -1

    return chord[index + 1]


def build_chord_labels(chord):
    labels = list(chord)
    degrees = list(chord)

    found_5th = False
    for index, interval in enumerate(chord):
        label = None
        degree = 1
        if index == 0:
            label = '1' # root is always 1
            degree = 1
        else:
            if interval == 1:
                label = 'b9'
                degree = 2
            elif interval == 2:
                label = '9'
                degree = 2
            elif interval == 3: # minor 3rd
                if lookahead(chord, index) == 4: # if there's a maj 3rd
                    label = '#9'
                    degree = 2
                else:
                    label = 'm3'
                    degree = 3
            elif interval == 4: # maj 3rd
                label = '3'
                degree = 3
            elif interval == 5: # perf 4th
                label = '11'
                degree = 4
            elif interval == 6: #11/b5
                if lookahead(chord, index) in (7,8): # if there's a perf 5th or #5
                    label = '#11'
                    degree = 4
                else:
                    label = 'b5'
                    degree = 5
                    found_5th = True
            elif interval == 7: # perf 5th
                label = '5'
                found_5th = True
                degree = 5
            elif interval == 8: # #5/b13
                if not found_5th:
                    label = '#5'
                    degree = 5
                else:
                    label = 'b13'
                    degree = 6
            elif interval == 9: # maj 6/13
                label = '13'
                degree = 6
            elif interval == 10:
                label = '7'
                degree = 7
            elif interval == 11:
                label = 'M7'
                degree = 7

        if not label:
            raise ValueError("Illegal chord interval {}".format(interval))

        labels[index] = label
        degrees[index] = degree

    return list(zip(chord, labels, degrees))

CHORD_REGEX = r'^([a-gA-G])(b|#)?([a-zA-Z0-9#]*)$'
chord_pattern = re.compile(CHORD_REGEX)

def parse_chord(chord):
    return chord_pattern.match(chord)

class Chords(object):
    # chords_file = ConfigParserProperty(0, 'harmonic_definitions', 'chords_file', 'app')

    def __init__(self, **kwargs):
        super(Chords, self).__init__(**kwargs)
        self.load_chords()

    def load_chords(self):
        chords_file = ConfigParser.get_configparser('app').get('harmonic_definitions', 'chords_file')
        # ConfigParser.get_configparser('app').get('fretboard', key)
        chords = toml.load(chords_file)

        chords = chords.get('chords')

        for s in chords.values():
            s.sort()

        self.chords = dict()

        for name, chord in chords.items():
            self.chords[name] = build_chord_labels(chord)

    def get_chord(self, name):
        return self.chords.get(name)


