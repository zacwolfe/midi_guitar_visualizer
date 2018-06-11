
import kivy
kivy.require('1.10.0') # replace with your current kivy version !

from kivy.app import App
from kivy.clock import Clock

from fretboard.fretboard import get_fretboard_adv_defaults, get_fretboard_defaults, get_window_defaults, get_harmonic_definitions_defaults
from fretboard.app_window import AppWindow
from fretboard.midi import get_midi_defaults

from dynamic_settings_item import SettingDynamicOptions
from kivy.uix.settings import SettingsWithSidebar
from color_picker import SettingColorPicker
from kivy.config import Config
from fretboard.midi_player import MidiPlayer


class FretboardNavigator(App):

    def __init__(self, **kwargs):
        super(FretboardNavigator, self).__init__(**kwargs)

    def build(self):
        self.settings_cls = SettingsWithSidebar
        self.midi_player = MidiPlayer()
        Config.set('kivy', 'KIVY_CLOCK', 'free_only')
        Config.write()
        app_window = AppWindow(self.midi_player)
        # fretb = Fretboard()
        def my_callback():
            app_window.fretboard.add_some_stuff()
            Clock.schedule_once(lambda dt:my_callback2(), 3 )

        def my_callback2():
            # app_window.fretboard.remove_some_stuff()
            app_window.fretboard.add_some_more_stuff()
            # Clock.schedule_once(lambda dt: my_callback2(), 3)

        Clock.schedule_once(lambda dt: my_callback(), 3)

        return app_window

    def on_stop(self):
        self.midi_player.stop()
        return True

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


if __name__ == '__main__':
    FretboardNavigator().run()