import kivy
kivy.require('1.10.0') # replace with your current kivy version !

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.widget import Widget

from kivy.graphics import Color, Ellipse, Line, Rectangle
from fretboard.fretboard import Fretboard
from fretboard.fretboard import get_fretboard_adv_defaults, get_fretboard_defaults, get_window_defaults
from fretboard.app_window import AppWindow
from fretboard.midi import Midi, NoteFilter
from kivy.uix.settings import SettingsWithTabbedPanel, SettingsWithSidebar
from color_picker import SettingColorPicker
from kivy.config import ConfigParser

# root = Builder.load_string('''
# FloatLayout:
#     canvas.before:
#         Color:
#             rgba: 0, 1, 0, 1
#         Rectangle:
#             # self here refers to the widget i.e FloatLayout
#             pos: self.pos
#             size: self.size
#     Button:
#         text: 'Hello World!!'
#         size_hint: .5, .5
#         pos_hint: {'center_x':.5, 'center_y': .5}
# ''')

# class MyPaintWidget(Widget):
#
#     def on_touch_down(self, touch):
#         with self.canvas:
#             Color(1, 1, 0)
#             d = 30.
#             Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))

class FretboardNavigator(App):

    def build(self):
        self.settings_cls = SettingsWithSidebar
        config = ConfigParser()
        config.read('myconfig.ini')
        s = SettingsWithSidebar()
        s.register_type('colorpicker', SettingColorPicker)
        s.add_kivy_panel()
        s.add_json_panel('Fretboard',
                         self.config,
                         filename='settings.json')

        # return Label(text='Hello World')
        # midi_port = 'Fishman TriplePlay TP Guitar'
        midi_port = None
        note_filter = NoteFilter()
        midi_config = Midi(note_filter, midi_port)
        app_window = AppWindow(midi_config)
        # fretb = Fretboard()
        def my_callback():
            app_window.fretboard.add_some_stuff()
            Clock.schedule_once(lambda dt:my_callback2(), 3 )

        def my_callback2():
            app_window.fretboard.remove_some_stuff()

        Clock.schedule_once(lambda dt: my_callback(), 3)
        # Clock.schedule_once(lambda dt:my_callback2, 6)
        return app_window
        # return MyPaintWidget()

    def build_config(self, config):
        config.setdefaults('fretboard', get_fretboard_defaults())
        config.setdefaults('fretboard_adv', get_fretboard_adv_defaults())
        config.setdefaults('window', get_window_defaults())


    def build_settings(self, settings):
        settings.register_type('colorpicker', SettingColorPicker)
        settings.add_json_panel('Fretboard',
                         self.config,
                         filename='settings.json')


    def on_config_change(self, config, section,
                         key, value):
        print(config, section, key, value)

    # def get_application_config(self):
    #     return super(FretboardNavigator, self).get_application_config(
    #         '~/.%(appname)s.ini')
if __name__ == '__main__':
    FretboardNavigator().run()