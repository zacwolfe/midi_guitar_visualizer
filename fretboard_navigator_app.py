import kivy
kivy.require('1.10.0') # replace with your current kivy version !

from kivy.app import App
from kivy.clock import Clock

from fretboard.fretboard import get_fretboard_adv_defaults, get_fretboard_defaults, get_window_defaults, get_harmonic_definitions_defaults
from fretboard.app_window import AppWindow
from fretboard.midi import Midi, NoteFilter, get_midi_defaults
from dynamic_settings_item import SettingDynamicOptions
from kivy.uix.settings import SettingsWithSidebar
from color_picker import SettingColorPicker
from kivy.config import Config
import constants

class FretboardNavigator(App):

    def build(self):
        self.settings_cls = SettingsWithSidebar

        Config.set('kivy', 'KIVY_CLOCK', 'free_all')
        Config.write()
        # midi_port = 'Fishman TriplePlay TP Guitar'
        app_window = AppWindow()
        # fretb = Fretboard()
        def my_callback():
            app_window.fretboard.add_some_stuff()
            Clock.schedule_once(lambda dt:my_callback2(), 3 )

        def my_callback2():
            # app_window.fretboard.remove_some_stuff()
            app_window.fretboard.add_some_more_stuff()
            # Clock.schedule_once(lambda dt: my_callback2(), 3)

        Clock.schedule_once(lambda dt: my_callback(), 3)

        # Clock.schedule_once(lambda dt:my_callback2, 6)
        return app_window

    def build_config(self, config):
        config.setdefaults('fretboard', get_fretboard_defaults())
        config.setdefaults('fretboard_adv', get_fretboard_adv_defaults())
        config.setdefaults('window', get_window_defaults())
        config.setdefaults('midi', get_midi_defaults())
        config.setdefaults('harmonic_definitions', get_harmonic_definitions_defaults())


    def build_settings(self, settings):
        settings.register_type('colorpicker', SettingColorPicker)
        settings.register_type('dynamic_options', SettingDynamicOptions)
        settings.add_json_panel('Fretboard', self.config, filename='settings.json')


    def on_config_change(self, config, section,
                         key, value):
        print('My huge ass has reconfigured....',config, section, key, value)
        if section == 'midi':
            self.root.reload_midi()
        elif section == 'scales':
            self.root.reload_scales()

    def on_start(self):
        print("I'm resumed")
        self.root.init_midi()
    # def get_application_config(self):
    #     return super(FretboardNavigator, self).get_application_config(
    #         '~/.%(appname)s.ini')
if __name__ == '__main__':
    FretboardNavigator().run()