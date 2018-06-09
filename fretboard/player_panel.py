from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.config import ConfigParser
from util.alert_dialog import Alert
import subprocess
import os
from kivy.properties import StringProperty, NumericProperty

class PlayerPanel(BoxLayout):
    play_label_text = StringProperty('')
    curr_line_num = NumericProperty(-1)
    play_button = None
    lines_map = dict()
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
        button_panel.center_x = self.center_y
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

        self.curr_line_text = Label(color=(1,0,0, 0.9), halign='left', id='curr_line', text='a-hole abundance', size_hint=(1, 0.1), font_size='26sp', outline_color=(0, 1, 0))
        self.mma_textarea = TextInput(text=self.initial_script, id='mma_textarea', size_hint=(1, 0.8))
        self.mma_textarea.bind(text=self.text_changed)
        self.mma_textarea.disabled_foreground_color = [0,0,0,1]
        self.mma_textarea.background_disabled_normal = ''


        self.add_widget(button_panel)
        self.add_widget(self.curr_line_text)
        self.add_widget(self.mma_textarea)

        tmp_dir = ConfigParser.get_configparser('app').get('fretboard_adv','mma_tmp_dir')
        self.init_tmp_dir(tmp_dir)
        self.tmp_mma_outfile = os.path.join(tmp_dir, 'tmp.mma')
        self.tmp_mid_outfile = os.path.join(tmp_dir, 'tmp.mid')

        self.mma_path = ConfigParser.get_configparser('app').get('fretboard_adv','mma_script_loc')
        self.needs_reload = False

        self.midi_config.set_player_callback(self.player_state_changed)
        self.midi_config.set_player_progress_callback(self.midi_file_progress)

        if self.initial_script:
            self.needs_reload = True


    def update_play_button_text(self, *args):
        self.play_button.text = self.play_label_text

    def text_changed(self, instance, text):
        print("text is {}".format(text))
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
            self.midi_config.set_midi_file(self.tmp_mid_outfile)
            self.needs_reload = False
            self.build_lines_map(txt)
        except subprocess.CalledProcessError as e:
            print("error with code {} and msg {}".format(e.returncode, e.output))
            Alert(title="Oops", text="Error caught writing file:{} \n{}".format(e.returncode, e.output))

    def build_lines_map(self, txt):
        self.lines_map.clear()
        lines = txt.splitlines(keepends=True)
        pointer = 0
        for idx, line in enumerate(lines):
            self.lines_map[idx] = (pointer, line)
            pointer += len(line)


    def player_state_changed(self, value):
        if value == 'paused':
            self.play_label_text = 'continue'
            self.mma_textarea.disabled = True
        elif value == 'playing':
            self.play_label_text = 'pause'
            self.mma_textarea.disabled = True
        else:
            self.play_label_text = 'play'
            self.mma_textarea.disabled=False

    def midi_file_progress(self, chord, scale_type, scale_key, scale_degree=None, line_num=None):
        if scale_degree is None:
            scale_degree = 1
        else:
            scale_degree = int(scale_degree)

        if chord == '/':
            chord = self.last_chord
        else:
            self.last_chord = chord

        self.fretboard.show_chord_tones(chord, scale_type, scale_key, scale_degree)

        if line_num is not None:
            line_num = int(line_num)
            if line_num != self.curr_line_num:
                self.curr_line_num = line_num

    def init_tmp_dir(self, dir):
        os.makedirs(dir, exist_ok=True)




