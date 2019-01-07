from kivy.uix.boxlayout import BoxLayout
import random
import winsound
from functools import partial
import copy
from kivy.clock import mainthread
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import pt
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget


class NoteTrainerPanel(BoxLayout):
    play_label_text = StringProperty('')
    current_note = StringProperty('', force_dispatch=True)
    play_button = None
    trainer_started = False
    selected_notes = set("ABCDEFG")
    current_mapping = None

    def __init__(self, fretboard, midi_config, tuning, **kwargs):
        super(NoteTrainerPanel, self).__init__(**kwargs)
        self.fretboard = fretboard
        self.midi_config = midi_config
        self.tuning = tuning
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
        self.note_checkbox_a = CheckBox(active=True)
        self.note_checkbox_a.bind(active=partial(self.note_checked, 'A'))
        notes_panel.add_widget(self.note_label_a)
        notes_panel.add_widget(self.note_checkbox_a)

        self.note_label_b = Label(halign='right', text='B:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_b = CheckBox(active=True)
        self.note_checkbox_b.bind(active=partial(self.note_checked, 'B'))
        notes_panel.add_widget(self.note_label_b)
        notes_panel.add_widget(self.note_checkbox_b)

        self.note_label_c = Label(halign='right', text='C:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_c = CheckBox(active=True)
        self.note_checkbox_c.bind(active=partial(self.note_checked, 'C'))
        notes_panel.add_widget(self.note_label_c)
        notes_panel.add_widget(self.note_checkbox_c)

        self.note_label_d = Label(halign='right', text='D:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_d = CheckBox(active=True)
        self.note_checkbox_d.bind(active=partial(self.note_checked, 'D'))
        notes_panel.add_widget(self.note_label_d)
        notes_panel.add_widget(self.note_checkbox_d)

        self.note_label_e = Label(halign='right', text='E:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_e = CheckBox(active=True)
        self.note_checkbox_e.bind(active=partial(self.note_checked, 'E'))
        notes_panel.add_widget(self.note_label_e)
        notes_panel.add_widget(self.note_checkbox_e)

        self.note_label_f = Label(halign='right', text='F:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_f = CheckBox(active=True)
        self.note_checkbox_f.bind(active=partial(self.note_checked, 'F'))
        notes_panel.add_widget(self.note_label_f)
        notes_panel.add_widget(self.note_checkbox_f)

        self.note_label_g = Label(halign='right', text='G:', font_size='16sp', color=(0, 0, 0, 1))
        self.note_checkbox_g = CheckBox(active=True)
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
        self.accidental_checkbox_none = CheckBox(group='accidentals', active=False)
        options_panel.add_widget(self.accidental_label_none)
        options_panel.add_widget(self.accidental_checkbox_none)

        self.accidental_label_sharp = Label(halign='right', text="#'s:", font_size='16sp', color=(0, 0, 0, 1))
        self.accidental_checkbox_sharp = CheckBox(group='accidentals')
        options_panel.add_widget(self.accidental_label_sharp)
        options_panel.add_widget(self.accidental_checkbox_sharp)

        self.accidental_label_flat = Label(halign='right', text="b's:", font_size='16sp', color=(0, 0, 0, 1))
        self.accidental_checkbox_flat = CheckBox(group='accidentals', active=True)
        options_panel.add_widget(self.accidental_label_flat)
        options_panel.add_widget(self.accidental_checkbox_flat)

        self.show_notes_label = Label(halign='right', text="show notes:", font_size='16sp', color=(0, 0, 0, 1))
        self.show_notes_checkbox = CheckBox(active=True)
        self.show_notes_checkbox.bind(active=self.show_notes)
        options_panel.add_widget(self.show_notes_label)
        options_panel.add_widget(self.show_notes_checkbox)

        self.require_all_label = Label(halign='right', text="require all:", font_size='16sp', color=(0, 0, 0, 1))
        self.require_all_checkbox = CheckBox()
        options_panel.add_widget(self.require_all_label)
        options_panel.add_widget(self.require_all_checkbox)

        self.error_sound_label = Label(halign='right', text="beep on error:", font_size='16sp', color=(0, 0, 0, 1))
        self.error_sound_checkbox = CheckBox()
        options_panel.add_widget(self.error_sound_label)
        options_panel.add_widget(self.error_sound_checkbox)

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
        elif keycode[1] == 'f1':
            App.get_running_app().open_settings()
        return True


    def show_notes(self, checkbox, value):
        self.fretboard.show_arpeggio_tones(value)

    def note_checked(self, note, checkbox, value):
        # print("note {}, checkbox {}, value {}".format(note, checkbox, value))
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
        self.current_mapping = self.cull_reference_strings(copy.deepcopy(self.fretboard.show_note(self.current_note)))

        # print("got a mapp {}".format(self.current_mapping))

    def cull_reference_strings(self, mapping):
        for string_num in list(mapping.keys()):
            if string_num > self.tuning.num_strings -1 or string_num < 0:
                del mapping[string_num]

        return mapping
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
        if not notes:
            return

        if len(notes) == 1:
            self.current_note = notes[0]
            return

        while True:
            note =random.choice(notes)
            if note != old_note:
                self.current_note = note
                return

    def is_hit(self, string_num, fret_num):
        if not self.current_mapping:
            return False

        mapping = self.current_mapping.get(string_num)
        if not mapping:
            return False

        for idx, fret in enumerate(mapping):
            if fret[0] == fret_num:
                if self.require_all_checkbox.active:
                    mapping.pop(idx)
                    if not mapping:
                        del self.current_mapping[string_num]
                    self.fretboard.hide_note(string_num, fret_num)
                return True

        return False

    # @mainthread
    def hit(self, string_num, fret_num, scale_degree, chord_degree):
        if not self.trainer_started:
            return

        # print("hit string {}:{}".format(string_num, fret_num))
        if self.is_hit(string_num, fret_num):
            if self.require_all_checkbox.active and self.current_mapping:
                print("still got {}".format(self.current_mapping))
                return
            # give a little delay before showing the next
            Clock.schedule_once(lambda dt: self.get_next_note(), .2)
            # self.get_next_note()
        elif self.error_sound_checkbox.active:
            winsound.Beep(261*2, 500)

