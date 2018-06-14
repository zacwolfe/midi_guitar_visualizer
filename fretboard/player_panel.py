from kivy.clock import mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.config import ConfigParser
from util.alert_dialog import Alert
import subprocess
import os
import re
from kivy.properties import StringProperty, NumericProperty
from . midi import PLAYER_STATE_STOPPED, PLAYER_STATE_PLAYING, PLAYER_STATE_PAUSED
from kivy.properties import ConfigParserProperty

TEMPO_REGEX = r'^tempo[\s]+([0-9]+)$'
TEMPO_PATTERN = re.compile(TEMPO_REGEX, re.IGNORECASE)

class PlayerPanel(BoxLayout):
    play_label_text = StringProperty('')
    curr_line_num = NumericProperty(-1)
    preload_chord_amt = ConfigParserProperty(0.0, 'midi', 'preload_chord_amt', 'app', val_type=float)
    common_chord_tone_amt = ConfigParserProperty(0.0, 'midi', 'common_chord_tone_amt', 'app', val_type=float)
    play_button = None
    lines_map = dict()
    current_tempo = 0
    initial_script = '''
// Sample tutorial file
// Fella Bird, try 2

Tempo 40
Groove Metronome2-4
 
   z * 1
 
Groove Rhumba
//Repeat
Volume mp
Cresc mf 4
Lyric CHORDS=Both

Repeat

1      F#M7  [<1>F#_major(0)]
2      GM7  [<1>G_major(0)]

repeatend

'''
    def __init__(self, fretboard, midi_config, **kwargs):
        super(PlayerPanel, self).__init__(**kwargs)
        self.fretboard = fretboard
        self.midi_config = midi_config
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        button_panel = BoxLayout(orientation='horizontal', size_hint_y=None, size_hint_x=1)
        button_panel.center_x = self.center_x
        self.play_button = Button(id='play',text='play', size=(200, 100), size_hint=(None, None), on_press=self.button_press)
        self.play_label_text = 'play'
        self.curr_line_num = -1
        self.bind(play_label_text=self.update_play_button_text)
        self.bind(curr_line_num=self.line_num_changed)
        rewind_button = Button(id='rewind', text='rewind', size=(200, 100), size_hint=(None, None), on_press=self.button_press)
        stop_button = Button(id='stop', text='stop', size=(200, 100), size_hint=(None, None), on_press=self.button_press)

        button_panel.add_widget(Widget())
        button_panel.add_widget(rewind_button)
        button_panel.add_widget(self.play_button)
        button_panel.add_widget(stop_button)
        button_panel.add_widget(Widget())


        # with self.curr_line_text.canvas:
        #     Color(0, 1, 0, 0.25)
        #     Rectangle(pos=self.curr_line_text.pos, size=self.curr_line_text.size)


        self.mma_textarea = TextInput(id='mma_textarea', size_hint=(1, 0.8), multiline=True)
        self.mma_textarea.bind(text=self.text_changed)
        self.mma_textarea.disabled_foreground_color = [0,0,0,1]
        self.mma_textarea.background_disabled_normal = ''

        self.chord_label = Label(halign='right',text='chord:', font_size='16sp', color=(0, 0, 0, 1))
        self.chord_input = TextInput(multiline=False, font_size='26sp')
        self.scale_type_label = Label(halign='right',text='scale type:', font_size='16sp', color=(0, 0, 0, 1))
        self.scale_type_input = TextInput(multiline=False, font_size='26sp')
        self.scale_key_label = Label(halign='right', text='scale key:', font_size='16sp', color=(0, 0, 0, 1))
        self.scale_key_input = TextInput(multiline=False, font_size='26sp')
        self.scale_degree_label = Label(halign='right', text='scale degree:', font_size='16sp', color=(0, 0, 0, 1))
        self.scale_degree_input = TextInput(multiline=False, font_size='26sp')
        self.show_scales_label = Label(halign='right', text='show scales:', font_size='16sp', color=(0, 0, 0, 1))
        self.show_scales_checkbox = CheckBox(active=True)
        self.show_scales_checkbox.bind(active=self.show_scales)
        self.show_chord_tones_label = Label(halign='right', text='show chord tones:', font_size='16sp', color=(0, 0, 0, 1))
        self.show_chord_tones_checkbox = CheckBox(active=True)
        self.show_chord_tones_checkbox.bind(active=self.show_chord_tones)

        self.apply_button = Button(id='apply', text='apply', on_press=self.button_press)

        # self.curr_line_text = Label(color=(1, 0, 0, 0.9), halign='left', id='curr_line', text='a-hole abundance', size_hint=(1, 0.1), font_size='26sp', outline_color=(0, 1, 0))
        harmonic_panel = GridLayout(cols=13, size_hint_y=0.05, height=90, size_hint_x=1, spacing=[10,10])

        # harmonic_panel.center_x = self.center_x
        harmonic_panel.add_widget(self.chord_label)
        harmonic_panel.add_widget(self.chord_input)
        harmonic_panel.add_widget(self.scale_type_label)
        harmonic_panel.add_widget(self.scale_type_input)
        harmonic_panel.add_widget(self.scale_key_label)
        harmonic_panel.add_widget(self.scale_key_input)
        harmonic_panel.add_widget(self.scale_degree_label)
        harmonic_panel.add_widget(self.scale_degree_input)
        harmonic_panel.add_widget(self.apply_button)
        harmonic_panel.add_widget(self.show_scales_label)
        harmonic_panel.add_widget(self.show_scales_checkbox)
        harmonic_panel.add_widget(self.show_chord_tones_label)
        harmonic_panel.add_widget(self.show_chord_tones_checkbox)

        with harmonic_panel.canvas:
            Color(0, 1, 0, 0.25)
            Rectangle(pos=harmonic_panel.pos, size=harmonic_panel.size)

        self.add_widget(button_panel)
        self.add_widget(harmonic_panel)
        self.add_widget(self.mma_textarea)

        tmp_dir = ConfigParser.get_configparser('app').get('fretboard_adv','mma_tmp_dir')
        self.init_tmp_dir(tmp_dir)
        self.tmp_mma_outfile = os.path.join(tmp_dir, 'tmp.mma')
        self.tmp_mid_outfile = os.path.join(tmp_dir, 'tmp.mid')

        self.mma_path = ConfigParser.get_configparser('app').get('fretboard_adv','mma_script_loc')
        self.needs_reload = False

        self.bind(preload_chord_amt=self.preload_chord_amt_changed)
        self.bind(common_chord_tone_amt=self.preload_chord_amt_changed)
        self.midi_config.set_player_callback(self.player_state_changed)
        self.midi_config.set_player_progress_callback(self.midi_file_progress)

        self.midi_config.preload_chord_amt = self.preload_chord_amt
        self.midi_config.common_chord_tone_amt = self.common_chord_tone_amt

        file_contents = None
        try:
            with open(self.tmp_mma_outfile, 'r') as lastfile:
                file_contents = lastfile.read()
        except FileNotFoundError:
            print("file {} doesn't yet exist".format(self.tmp_mma_outfile))

        if not file_contents:
            file_contents = self.initial_script

        self.mma_textarea.text = file_contents

        if self.initial_script:
            self.needs_reload = True

    def set_inputs_disabled(self, value):
        self.mma_textarea.disabled = value
        self.chord_input.disabled = value
        self.scale_type_input.disabled = value
        self.scale_key_input.disabled = value
        self.scale_degree_input.disabled = value
        self.apply_button.disabled = value
        self.scale_type_input.disabled = value
        self.scale_type_input.disabled = value
        self.scale_type_input.disabled = value


    def show_scales(self, checkbox, value):
        self.fretboard.show_scales(value)

    def show_chord_tones(self, checkbox, value):
        self.fretboard.show_arpeggio_tones(value)

    def update_play_button_text(self, *args):
        self.play_button.text = self.play_label_text

    def text_changed(self, instance, text):
        print("text is {}".format(text))
        self.needs_reload = True

    def preload_chord_amt_changed(self, *args):
        self.midi_config.preload_chord_amt = self.preload_chord_amt
        self.midi_config.common_chord_tone_amt = self.common_chord_tone_amt
        self.needs_reload = True

    def line_num_changed(self, *args):
        try:
            l = self.lines_map[self.curr_line_num - 1]

            self.mma_textarea.select_text(l[0], l[0] + len(l[1]))
        except:
            print("Couldn't select text at {}".format(self.curr_line_num))
            self.mma_textarea.select_text(0,0)

    def button_press(self, button):
        txt = 'mine ass {} has thrived for many a year'.format(button.id)
        if button.id == 'play':
            if self.needs_reload:
                self.reload_mma()
            if not self.needs_reload:
                self.play_midi()
        elif button.id == 'stop':
            self.stop_playing_midi()
        elif button.id == 'apply':
            self.apply_harmonic_setting()
        # self.curr_line_text.text = txt
        # self.curr_line_text.texture_update()
        # print(txt)

    def play_midi(self):
        self.midi_config.play()

    def stop_playing_midi(self):
        self.midi_config.stop()

    def reload_mma(self):
        txt = self.mma_textarea.text
        with open(self.tmp_mma_outfile, "w") as file:
            file.write(txt)
        try:
            subprocess.run("{} -f {} {}".format(self.mma_path, self.tmp_mid_outfile, self.tmp_mma_outfile), shell=True, check=True)
            self.build_lines_map(txt)
            self.midi_config.set_midi_file(self.tmp_mid_outfile, self.current_tempo)
            self.needs_reload = False

        except subprocess.CalledProcessError as e:
            print("error with code {} and msg {}".format(e.returncode, e.output))
            Alert(title="Oops", text="Error caught writing file:{} \n{}".format(e.returncode, e.output))

    def build_lines_map(self, txt):
        self.lines_map.clear()
        lines = txt.splitlines(keepends=True)
        pointer = 0
        self.current_tempo = 0
        for idx, line in enumerate(lines):
            self.lines_map[idx] = (pointer, line)
            pointer += len(line)
            m = TEMPO_PATTERN.match(line)
            if m:
                self.current_tempo = m.group(1)



    def player_state_changed(self, value):
        if value == PLAYER_STATE_PAUSED:
            self.play_label_text = 'continue'
            self.set_inputs_disabled(True)
        elif value == PLAYER_STATE_PLAYING:
            self.play_label_text = 'pause'
            self.set_inputs_disabled(True)
        else:
            self.play_label_text = 'play'
            self.set_inputs_disabled(False)



    @mainthread
    def midi_file_progress(self, chord, scale_type, scale_key, scale_degree=None, line_num=None, pre_chord=False):

        if scale_degree is None:
            scale_degree = 1
        else:
            scale_degree = int(scale_degree)

        if pre_chord:
            self.fretboard.show_common_chord_tones(self.last_chord if chord == '/' else chord, scale_type, scale_key, scale_degree)
        else:

            if chord == '/':
                chord = self.last_chord
            else:
                self.last_chord = chord

            self.fretboard.show_chord_tones(chord, scale_type, scale_key, scale_degree)

            if line_num is not None:
                line_num = int(line_num)
                if line_num != self.curr_line_num:
                    self.curr_line_num = line_num

            if chord:
                self.chord_input.text = chord
            # self.chord_input.texture_update()

            if scale_type:
                self.scale_type_input.text = scale_type
            # self.scale_type_input.texture_update()

            if scale_key:
                self.scale_key_input.text = scale_key
            # self.scale_key_input.texture_update()

            if scale_degree is not None:
                self.scale_degree_input.text = str(scale_degree)
        # self.scale_degree_input.texture_update()

    def apply_harmonic_setting(self):
        try:
            self.fretboard.show_chord_tones(self.chord_input.text, self.scale_type_input.text, self.scale_key_input.text, int(self.scale_degree_input.text))
        except Exception as e:
            Alert(title="Oops", text="Couldn't understand harmonic settings:{}".format(str(e)))

    def init_tmp_dir(self, dir):
        os.makedirs(dir, exist_ok=True)




