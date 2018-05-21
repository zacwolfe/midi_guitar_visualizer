import toml
from kivy.config import ConfigParser
from kivy.properties import ConfigParserProperty

scale_systems_file = 'scale_systems.toml'

class Scales(object):
    scales_file = ConfigParserProperty(0, 'scales', 'scale_system_file', 'app')

    def __init__(self, **kwargs):
        super(Scales, self).__init__(**kwargs)
        self.load_scales()

    def load_scales(self):
        # ConfigParser.get_configparser('app').get('fretboard', key)
        scale_systems = toml.load(self.scales_file)

        systems = scale_systems.get('systems')
        self.scales = scale_systems.get('scales') + systems

        for s in self.scales.values():
            s.sort()


    def get_scale(self, name):
        return self.scales.get(name)


