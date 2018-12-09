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
from util.input_dialog import open_saveas_dialog
import subprocess
import os
import re
from kivy.properties import StringProperty, NumericProperty
from kivy.properties import ConfigParserProperty
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from shutil import copyfile
from os.path import basename
from kivy.metrics import pt
from functools import partial
import random


class NoteTrainerPanel(BoxLayout):
    play_label_text = StringProperty('')
    current_note = StringProperty('')
    play_button = None
    trainer_started = False
    selected_notes = set()
    current_mapping = None

    def __init__(self, fretboard, midi_config, **kwargs):
        super(NoteTrainerPanel, self).__init__(**kwargs)
        self.fretboard = fretboard
        self.midi_config = midi_config
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        button_panel = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        button_panel.height = pt(20)
        button_panel.center_x = self.center_x
        self.play_button = Button(id='play',text='play', on_press=self.button_press, size_hint=(None,None))
        # self.play_button.height = pt(20)

        self.play_label_text = 'play'
        self.curr_line_num = -1
        self.bind(play_label_text=self.update_play_button_text)
        self.bind(current_note=self.update_current_note)

        button_panel.add_widget(Widget())
        # button_panel.add_widget(rewind_button)
        button_panel.add_widget(self.play_button)
        # button_panel.add_widget(stop_button)
        button_panel.add_widget(Widget())

        self.add_widget(button_panel)

        notes_container = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        notes_panel = GridLayout(cols=14, row_force_default=True, row_default_height=40)

        self.note_label_a = Label(halign='right', text='A:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_a = CheckBox()
        self.note_checkbox_a.bind(active=partial(self.note_checked, 'A'))
        notes_panel.add_widget(self.note_label_a)
        notes_panel.add_widget(self.note_checkbox_a)

        self.note_label_b = Label(halign='right', text='B:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_b = CheckBox()
        self.note_checkbox_b.bind(active=partial(self.note_checked, 'B'))
        notes_panel.add_widget(self.note_label_b)
        notes_panel.add_widget(self.note_checkbox_b)

        self.note_label_c = Label(halign='right', text='C:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_c = CheckBox()
        self.note_checkbox_c.bind(active=partial(self.note_checked, 'C'))
        notes_panel.add_widget(self.note_label_c)
        notes_panel.add_widget(self.note_checkbox_c)

        self.note_label_d = Label(halign='right', text='D:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_d = CheckBox()
        self.note_checkbox_d.bind(active=partial(self.note_checked, 'D'))
        notes_panel.add_widget(self.note_label_d)
        notes_panel.add_widget(self.note_checkbox_d)

        self.note_label_e = Label(halign='right', text='E:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_e = CheckBox()
        self.note_checkbox_e.bind(active=partial(self.note_checked, 'E'))
        notes_panel.add_widget(self.note_label_e)
        notes_panel.add_widget(self.note_checkbox_e)

        self.note_label_f = Label(halign='right', text='F:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_f = CheckBox()
        self.note_checkbox_f.bind(active=partial(self.note_checked, 'F'))
        notes_panel.add_widget(self.note_label_f)
        notes_panel.add_widget(self.note_checkbox_f)

        self.note_label_g = Label(halign='right', text='G:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_g = CheckBox()
        self.note_checkbox_g.bind(active=partial(self.note_checked, 'G'))
        notes_panel.add_widget(self.note_label_g)
        notes_panel.add_widget(self.note_checkbox_g)

        notes_container.add_widget(Widget())
        notes_container.add_widget(notes_panel)
        notes_container.add_widget(Widget())
        self.add_widget(notes_container)

        options_container = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        options_panel = GridLayout(cols=14, row_force_default=True, row_default_height=40)

        self.accidental_label_none = Label(halign='right', text="none:", font_size='16sp', color=(0, 0, 0, 1))
        self.accidental_checkbox_none = CheckBox(group='accidentals', active=True)
        options_panel.add_widget(self.accidental_label_none)
        options_panel.add_widget(self.accidental_checkbox_none)

        self.accidental_label_sharp = Label(halign='right', text="#'s:", font_size='16sp', color=(0, 0, 0, 1))
        self.accidental_checkbox_sharp = CheckBox(group='accidentals')
        options_panel.add_widget(self.accidental_label_sharp)
        options_panel.add_widget(self.accidental_checkbox_sharp)

        self.accidental_label_flat = Label(halign='right', text="b's:", font_size='16sp', color=(0, 0, 0, 1))
        self.accidental_checkbox_flat = CheckBox(group='accidentals')
        options_panel.add_widget(self.accidental_label_flat)
        options_panel.add_widget(self.accidental_checkbox_flat)

        self.show_notes_label = Label(halign='right', text="show notes:", font_size='16sp', color=(0, 0, 0, 1))
        self.show_notes_checkbox = CheckBox()
        options_panel.add_widget(self.show_notes_label)
        options_panel.add_widget(self.show_notes_checkbox)

        self.require_all_label = Label(halign='right', text="require all:", font_size='16sp', color=(0, 0, 0, 1))
        self.require_all_checkbox = CheckBox()
        options_panel.add_widget(self.require_all_label)
        options_panel.add_widget(self.require_all_checkbox)

        options_container.add_widget(Widget())
        options_container.add_widget(options_panel)
        options_container.add_widget(Widget())
        self.add_widget(options_container)

        self.current_note_label = Label(halign='center', text="?", font_size='340sp', color=(0, 0.1, 0.8, 1), size_hint=(1, .7))
        self.add_widget(self.current_note_label)

        fretboard.set_target_tone_callback(self)

    def key_pressed(self, keyboard, keycode, text, modifiers):
        self._on_keyboard_down(keyboard, keycode, text, modifiers)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print("key down shit biggler {} and {} with modifiers {}".format(keycode, text, modifiers))
        if keycode[1] == 'spacebar':
            self.play_pressed()
        return True


    def note_checked(self, note, checkbox, value):
        print("note {}, checkbox {}, value {}".format(note, checkbox, value))
        if value:
            self.selected_notes.add(note)
        else:
            self.selected_notes.remove(note)


    def show_pattern_mapping(self, checkbox, value):
        self.fretboard.track_patterns(value)

    def update_play_button_text(self, *args):
        self.play_button.text = self.play_label_text

    def update_current_note(self, *args):
        self.current_note_label.text = self.current_note
        self.current_mapping = self.fretboard.show_note(self.current_note)
        print("got a mapp {}".format(self.current_mapping))

    def button_press(self, button):
        if button.id == 'play':
            self.play_pressed()

    def play_pressed(self):
        self.trainer_started = not self.trainer_started
        if self.trainer_started:
            self.play_label_text = 'stop'
            self.start_trainer()
        else:
            self.play_label_text = 'play'
            self.stop_trainer()

    def stop_trainer(self):
        pass

    def get_avail_notes(self):
        notes = list(self.selected_notes)
        if not notes:
            return None
        for note in self.selected_notes:
            if self.accidental_checkbox_flat.active:
                if note not in ['C', 'F']:
                    notes.append(note + 'b')
            elif self.accidental_checkbox_sharp.active:
                if note not in ['B', 'E']:
                    notes.append(note + '#')

        return notes

    def start_trainer(self):
        self.get_next_note()

    def get_next_note(self):
        old_note = self.current_note
        notes = self.get_avail_notes()
        print("got notes {}".format(notes))
        if not notes:
            return

        if len(notes) == 1:
            return notes[0]

        while True:
            note =random.choice(notes)
            if note != old_note:
                self.current_note = note
                return

    def hit(self, string_num, fret_num, scale_degree, chord_degree):
        if not self.trainer_started:
            return

        if chord_degree is not None:
            self.get_next_note()

