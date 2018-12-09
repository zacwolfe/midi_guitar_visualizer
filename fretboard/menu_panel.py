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
from . midi import PLAYER_STATE_STOPPED, PLAYER_STATE_PLAYING, PLAYER_STATE_PAUSED
from kivy.properties import ConfigParserProperty
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.metrics import pt
from shutil import copyfile
from os.path import basename
from kivy.uix.screenmanager import ScreenManager, Screen

class MenuPanel(BoxLayout):
    sm = ScreenManager()

    def __init__(self, fretboard, player_panel, note_trainer_panel, **kwargs):
        super(MenuPanel, self).__init__(**kwargs)
        self.fretboard = fretboard
        self.player_panel = player_panel
        self.note_trainer_panel = note_trainer_panel
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10


        button_panel = BoxLayout(orientation='horizontal', size_hint=(1, None))
        button_panel.height = pt(20)
        button_panel.center_x = self.center_x

        player_button = Button(id='player', text='player', on_release=self.button_press)
        trainer_button = Button(id='notetrainer', text='note trainer', on_release=self.button_press)

        button_panel.add_widget(player_button)
        button_panel.add_widget(trainer_button)
        self.add_widget(button_panel)
        self.add_widget(self.sm)

        player_screen = Screen(name='player')
        player_screen.add_widget(player_panel)
        note_trainer_screen = Screen(name='notetrainer')
        note_trainer_screen.add_widget(note_trainer_panel)

        self.sm.add_widget(player_screen)
        self.sm.add_widget(note_trainer_screen)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print("key down shit biggler {} and {} with modifiers {}".format(keycode, text, modifiers))
        if keycode[1] == 'spacebar':
            self.player_panel.key_pressed(keycode[1])

        return True

    def button_press(self, button):
        txt = 'mine asser {} has thrived for many a year'.format(button.id)
        self.sm.current = button.id




