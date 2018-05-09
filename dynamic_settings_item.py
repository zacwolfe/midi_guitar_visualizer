from kivy.uix.settings import SettingItem, SettingOptions
from kivy.properties import StringProperty

import importlib

class SettingDynamicOptions(SettingOptions):
    '''Implementation of an option list that creates the items in the possible
    options list by calling an external method, that should be defined in
    the settings class.
    '''

    function_string = StringProperty()
    '''The function's name to call each time the list should be updated.
    It should return a list of strings, to be used for the options.
    '''

    def _create_popup(self, instance):
        # Update the options
        mod_name, func_name = self.function_string.rsplit('.',1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        self.options = func()

        # Call the parent __init__
        super(SettingDynamicOptions, self)._create_popup(instance)