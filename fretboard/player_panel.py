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

class PlayerPanel(BoxLayout):

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

 
1      F / Am Gm [<1>F_ionian <2>F_ionian <3>major(3) <4>dorian]
2      F / Am Gm [<1>A_diminished <2>A_diminished <3>Db_melodicminor <4>Db_melodicminor]
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
        play_button = Button(id='play',text='play', size=(200, 100), size_hint=(None, None), on_press=self.button_press)
        rewind_button = Button(id='rewind', text='rewind', size=(200, 100), size_hint=(None, None), on_press=self.button_press)
        stop_button = Button(id='stop', text='stop', size=(200, 100), size_hint=(None, None), on_press=self.button_press)

        button_panel.add_widget(Widget())
        button_panel.add_widget(rewind_button)
        button_panel.add_widget(play_button)
        button_panel.add_widget(stop_button)
        button_panel.add_widget(Widget())


        # with self.curr_line_text.canvas:
        #     Color(0, 1, 0, 0.25)
        #     Rectangle(pos=self.curr_line_text.pos, size=self.curr_line_text.size)

        self.curr_line_text = Label(color=(1,0,0, 0.9), halign='left', id='curr_line', text='a-hole abundance', size_hint=(1, 0.1), font_size='26sp', outline_color=(0, 1, 0))
        self.mma_textarea = TextInput(text=self.initial_script, id='mma_textarea', size_hint=(1, 0.8))
        self.mma_textarea.bind(text=self.text_changed)


        self.add_widget(button_panel)
        self.add_widget(self.curr_line_text)
        self.add_widget(self.mma_textarea)

        tmp_dir = ConfigParser.get_configparser('app').get('fretboard_adv','mma_tmp_dir')
        self.init_tmp_dir(tmp_dir)
        self.tmp_mma_outfile = os.path.join(tmp_dir, 'tmp.mma')
        self.tmp_mid_outfile = os.path.join(tmp_dir, 'tmp.mid')

        self.mma_path = ConfigParser.get_configparser('app').get('fretboard_adv','mma_script_loc')
        self.needs_reload = False

    def text_changed(self, instance, text):
        print("text is {}".format(text))
        self.needs_reload = True

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
        except subprocess.CalledProcessError as e:
            print("error with code {} and msg {}".format(e.returncode, e.output))
            Alert(title="Oops", text="Error caught writing file:{} \n{}".format(e.returncode, e.output))




    def init_tmp_dir(self, dir):
        os.makedirs(dir, exist_ok=True)




