import kivy
kivy.require('1.10.0') # replace with your current kivy version !

from kivy.app import App
from kivy.clock import Clock

from fretboard.fretboard import get_fretboard_adv_defaults, get_fretboard_defaults, get_window_defaults
from fretboard.app_window import AppWindow
from fretboard.midi import Midi, NoteFilter
from kivy.uix.settings import SettingsWithSidebar
from color_picker import SettingColorPicker

class FretboardNavigator(App):

    def build(self):
        self.settings_cls = SettingsWithSidebar

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