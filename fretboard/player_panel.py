import os
import re
import subprocess
from os.path import basename
from shutil import copyfile

from kivy.app import App
from kivy.clock import mainthread
from kivy.config import ConfigParser
from kivy.core.window import Window
from kivy.properties import ConfigParserProperty
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView

from util.alert_dialog import Alert
from util.input_dialog import open_saveas_dialog
from .midi import PLAYER_STATE_STOPPED, PLAYER_STATE_PLAYING, PLAYER_STATE_PAUSED

# import MMA.main

TEMPO_REGEX = r'^tempo[\s]+([0-9]+)$'
TEMPO_PATTERN = re.compile(TEMPO_REGEX, re.IGNORECASE)
MAX_BAR_COUNT = 1000
class PlayerPanel(BoxLayout):
    play_label_text = StringProperty('')
    curr_line_num = NumericProperty(-1)
    preload_chord_amt = ConfigParserProperty(0.0, 'midi', 'preload_chord_amt', 'app', val_type=float)
    common_chord_tone_amt = ConfigParserProperty(0.0, 'midi', 'common_chord_tone_amt', 'app', val_type=float)
    play_button = None
    player_state = PLAYER_STATE_STOPPED
    lines_map = dict()
    files_list = list()
    current_tempo = 0
    last_chord = None
    current_filename = None
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
        button_panel = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))
        button_panel.center_x = self.center_x
        self.play_button = Button(id='play',text='play', size=(200, 100), size_hint=(0.1, 1), on_press=self.button_press)
        self.play_label_text = 'play'
        self.curr_line_num = -1
        self.bind(play_label_text=self.update_play_button_text)
        self.bind(curr_line_num=self.line_num_changed)
        rewind_button = Button(id='rewind', text='rewind', size=(200, 100), size_hint=(0.1, 1), on_press=self.button_press)
        stop_button = Button(id='stop', text='stop', size=(200, 100), size_hint=(0.1, 1), on_press=self.button_press)

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

        # self.scrollview = ScrollView(size_hint=(1, 0.8))
        # self.scrollview.add_widget(self.mma_textarea)

        checkbox_size_hint = 0.2
        font_size = '22sp'
        self.chord_label = Label(halign='right',text='chord:', font_size='16sp', color=(0, 0, 0, 1), size_hint_x=0.5)
        self.chord_input = TextInput(multiline=False, font_size=font_size)
        self.scale_type_label = Label(halign='right',text='scale type:', font_size='16sp', color=(0, 0, 0, 1), size_hint_x=0.6)
        self.scale_type_input = TextInput(multiline=False, font_size=font_size, size_hint_x=1.5)
        self.scale_key_label = Label(halign='right', text='scale key:', font_size='16sp', color=(0, 0, 0, 1), size_hint_x=0.6)
        self.scale_key_input = TextInput(multiline=False, font_size=font_size, size_hint_x=0.4)
        self.scale_degree_label = Label(halign='right', text='scale degree:', font_size='16sp', color=(0, 0, 0, 1), size_hint_x=0.7)
        self.scale_degree_input = TextInput(multiline=False, font_size=font_size, size_hint_x=0.4)
        self.show_scales_label = Label(halign='right', text='scales:', font_size='16sp', color=(0, 0, 0, 1), size_hint_x=0.5)
        self.show_scales_checkbox = CheckBox(active=True, size_hint_x=checkbox_size_hint)
        self.show_scales_checkbox.bind(active=self.show_scales)
        self.show_chord_tones_label = Label(halign='right', text='chord tones:', font_size='16sp', color=(0, 0, 0, 1), size_hint_x=0.7)
        self.show_chord_tones_checkbox = CheckBox(active=True, size_hint_x=checkbox_size_hint)
        self.show_chord_tones_checkbox.bind(active=self.show_chord_tones)

        self.show_pattern_mapping_label = Label(halign='right', text='pattern mapping:', font_size='16sp', color=(0, 0, 0, 1))
        self.show_pattern_mapping_checkbox = CheckBox(active=True, size_hint_x=checkbox_size_hint)
        self.show_pattern_mapping_checkbox.bind(active=self.show_pattern_mapping)

        self.show_common_chord_tones_label = Label(halign='right', text='common tones:', font_size='16sp', color=(0, 0, 0, 1))
        self.show_common_chord_tones_checkbox = CheckBox(active=True, size_hint_x=checkbox_size_hint)
        self.show_common_chord_tones_checkbox.bind(active=self.show_common_chord_tones)

        self.apply_button = Button(id='apply', text='apply', on_press=self.button_press, size_hint_x=0.4)

        # self.curr_line_text = Label(color=(1, 0, 0, 0.9), halign='left', id='curr_line', text='a-hole abundance', size_hint=(1, 0.1), font_size='26sp', outline_color=(0, 1, 0))
        harmonic_panel = GridLayout(cols=17, size_hint_y=0.05, height=90, size_hint_x=1, spacing=[10,10])

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

        harmonic_panel.add_widget(self.show_pattern_mapping_label)
        harmonic_panel.add_widget(self.show_pattern_mapping_checkbox)

        harmonic_panel.add_widget(self.show_common_chord_tones_label)
        harmonic_panel.add_widget(self.show_common_chord_tones_checkbox)

        save_button = Button(id='save', text='save', on_press=self.button_press, size_hint_x=0.1)
        self.saved_dropdown = DropDown(size_hint_x=0.7)
        save_panel = BoxLayout(orientation='horizontal', size_hint_y=.05, size_hint_x=1, minimum_height=100)

        saved_button = Button(text='-- Select Saved --', size_hint_x=1)

        # show the dropdown menu when the main button is released
        # note: all the bind() calls pass the instance of the caller (here, the
        # mainbutton instance) as the first argument of the callback (here,
        # dropdown.open.).
        saved_button.bind(on_release=self.saved_dropdown.open)

        # one last thing, listen for the selection in the dropdown list and
        # assign the data to the button text.
        self.saved_dropdown.bind(on_select=self.load_saved)

        self.saved_button = saved_button
        save_panel.add_widget(Widget())
        save_panel.add_widget(save_button)
        save_panel.add_widget(saved_button)
        save_panel.center_x = self.center_x
        save_panel.add_widget(Widget())

        # with harmonic_panel.canvas:
        #     Color(0, 1, 0, 0.25)
        #     Rectangle(pos=harmonic_panel.pos, size=harmonic_panel.size)

        self.add_widget(button_panel)
        self.add_widget(harmonic_panel)
        self.add_widget(save_panel)
        self.add_widget(self.mma_textarea)
        # self.add_widget(self.scrollview)

        tmp_dir = ConfigParser.get_configparser('app').get('fretboard_adv','mma_tmp_dir')
        self.init_tmp_dir(tmp_dir)
        self.tmp_mma_outfile = os.path.join(tmp_dir, 'tmp.mma')
        self.tmp_mid_outfile = os.path.join(tmp_dir, 'tmp.mid')
        self.tmp_dir = tmp_dir

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

        self.showing_scales = True
        if self.initial_script:
            self.needs_reload = True

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.load_saved_files()
        self.reload_saved_dropdown()

        def on_parent(self, widget, parent):
            self.mma_textarea.focus = True

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None


    def key_pressed(self, keyboard, keycode, text, modifiers):
        self._on_keyboard_down(keyboard, keycode, text, modifiers)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print("key down shit biggler {} and {} with modifiers {}".format(keycode, text, modifiers))
        if keycode[1] == 'spacebar':
            if self.player_state == PLAYER_STATE_STOPPED:
                self.play_pressed()
            elif self.player_state == PLAYER_STATE_PLAYING:
                if modifiers and modifiers[0] == 'alt':
                    self.play_pressed()
                else:
                    self.stop_playing_midi()
        elif keycode[1] == 'f1':
            App.get_running_app().open_settings()
        # if keycode[1] == 'w':
        #     self.player1.center_y += 10
        # elif keycode[1] == 's':
        #     self.player1.center_y -= 10
        # elif keycode[1] == 'up':
        #     self.player2.center_y += 10
        # elif keycode[1] == 'down':
        #     self.player2.center_y -= 10
        return True

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
        self.showing_scales = value
        self.fretboard.show_scales(value)

    def show_chord_tones(self, checkbox, value):
        self.fretboard.show_arpeggio_tones(value)

    def show_pattern_mapping(self, checkbox, value):
        self.fretboard.track_patterns(value)

    def show_common_chord_tones(self, checkbox, value):
        self.fretboard.set_common_chord_tones_visible(value)

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
            self.mma_textarea.cursor = (0, self.curr_line_num - 1)
        except:
            print("Couldn't select text at {}".format(self.curr_line_num))
            self.mma_textarea.select_text(0,0)

    def button_press(self, button):
        txt = 'mine ass {} has thrived for many a year'.format(button.id)
        if button.id == 'play':
            self.play_pressed()
        elif button.id == 'stop':
            self.stop_playing_midi()
        elif button.id == 'apply':
            self.apply_harmonic_setting()
        elif button.id == 'save':
            self.do_save_as()
        # self.curr_line_text.text = txt
        # self.curr_line_text.texture_update()
        # print(txt)


    def do_save_as(self):
        def on_save(file):
            print("da file wuz {}".format(file))
            if self.needs_reload:
                self.reload_mma()
            print("fugging outfile is {}".format(self.tmp_mma_outfile))
            copyfile(self.tmp_mma_outfile, os.path.join(self.tmp_dir, file + '.mma'))
            copyfile(self.tmp_mid_outfile, os.path.join(self.tmp_dir, file + '.mid'))
            self.reload_saved_dropdown()
            self.load_saved(self.saved_dropdown, os.path.join(self.tmp_dir, file + '.mma'))

        open_saveas_dialog(current_name=os.path.splitext(basename(self.current_filename))[0] if self.current_filename else '', on_save=on_save)


    def load_saved_files(self):
        self.files_list = []
        for file in os.listdir(self.tmp_dir):
            if file.endswith(".mma") and file != 'tmp.mma':
                f = os.path.join(self.tmp_dir, file).replace("\\","/")
                self.files_list.append(f)

    def reload_saved_dropdown(self):
        self.saved_dropdown.clear_widgets()
        for file in self.files_list:
            # When adding widgets, we need to specify the height manually
            # (disabling the size_hint_y) so the dropdown can calculate
            # the area it needs.

            btn = Button(text=file, size_hint_y=None, height=44)

            # for each button, attach a callback that will call the select() method
            # on the dropdown. We'll pass the text of the button as the data of the
            # selection.
            btn.bind(on_release=lambda btn: self.saved_dropdown.select(btn.text))

            # then add the button inside the dropdown
            self.saved_dropdown.add_widget(btn)

    def load_saved(self, widget, selected, *args):
        print("selected was {} of type {} wit args {}".format(selected, type(selected), args))
        setattr(self.saved_button, 'text', selected)
        if self.load_file_contents(selected):
            self.current_filename = selected
        else:
            Alert(title="Oops", text="Couldn't load file:{}".format(selected))


    def load_file_contents(self, file):
        try:
            with open(file, 'r') as f:
                file_contents = f.read()
        except FileNotFoundError:
            print("file {} doesn't exist".format(file))
            return None

        copyfile(file, self.tmp_mma_outfile)

        self.mma_textarea.text = file_contents
        self.build_lines_map(file_contents)
        mid_name, _ = os.path.splitext(file)
        mid_name += ".mid"
        print("midi file name is {}".format(mid_name))
        try:
            self.midi_config.set_midi_file(mid_name, self.current_tempo)
            self.needs_reload = False
            copyfile(mid_name, self.tmp_mid_outfile)
        except FileNotFoundError:
            print("midi file {} doesn't exist".format(mid_name))
            self.needs_reload = True

        return file


    def play_pressed(self):
        if self.needs_reload:
            self.reload_mma()
        if not self.needs_reload:
            self.play_midi()

    def play_midi(self):
        self.midi_config.play()

    def stop_playing_midi(self):
        self.midi_config.stop()

    def reload_mma(self):
        txt = self.mma_textarea.text
        with open(self.tmp_mma_outfile, "w") as file:
            file.write(txt)
        try:
            subprocess.run("python {} -m {} -f {} {}".format(self.mma_path, MAX_BAR_COUNT, self.tmp_mid_outfile, self.tmp_mma_outfile), shell=True, check=True)
            # import sys
            # import runpy
            #
            # root = 'D:\gitrepo\midi_guitar_visualizer'
            # path = os.getcwd()
            # os.chdir(root + '\mma_main')
            #
            # sys.argv = ['', '-m', MAX_BAR_COUNT, '-f',root + '/' + self.tmp_mid_outfile, root + '/' + self.tmp_mma_outfile ]
            # runpy.run_path(root + '\mma_main\mma.py', run_name='__main__')
            # os.chdir(root)
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
        self.player_state = value
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

        if not self.showing_scales:
            scale_type = None
            scale_key = None

        if pre_chord:
            if self.last_chord != chord:
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
            self.fretboard.show_chord_tones(self.chord_input.text, self.scale_type_input.text, self.scale_key_input.text, 0 if not self.scale_degree_input.text else int(self.scale_degree_input.text))
        except Exception as e:
            print(e)
            Alert(title="Oops", text="Couldn't understand harmonic settings:{}".format(str(e)))

    def init_tmp_dir(self, dir):
        os.makedirs(dir, exist_ok=True)




