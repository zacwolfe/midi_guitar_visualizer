import unittest
from scales.scales import Scales, Chords, Patterns, chord_label_to_interval, parse_chord
from fretboard.tunings import StandardTuning, Tuning, P4Tuning
from fretboard.fretboard import get_fretboard_adv_defaults, get_fretboard_defaults, get_window_defaults, get_harmonic_definitions_defaults
import json
from kivy.config import ConfigParser

class P4TuningTest(unittest.TestCase):

    def setUp(self):
        config = ConfigParser(name='app')
        config.setdefaults('fretboard', get_fretboard_defaults())
        config.setdefaults('fretboard_adv', get_fretboard_adv_defaults())
        config.setdefaults('window', get_window_defaults())
        # config.setdefaults('midi', get_midi_defaults())
        config.setdefaults('harmonic_definitions', get_harmonic_definitions_defaults())
        self.tuning = P4Tuning(22)
        self.scale_config = Scales()
        self.chords_config = Chords()
        self.pattern_config = Patterns()

    def tearDown(self):
        pass

    def test_pattern(self):
        chord = 'GM7'
        scale_name = 'major'
        scale_key = 'G'
        scale_degree = 0

        m = parse_chord(chord)
        if not m:
            return

        chord_tone = m[1]
        if m[2]:
            chord_tone += m[2]
        chord_type = m[3]
        chord_spec = self.chords_config.get_chord(chord_type)
        if not chord_spec:
            raise ValueError("Chord type {} not found".format(chord_type))
        scale = None
        if scale_name:
            scale = self.scale_config.get_scale(scale_name)

        mappings = self.tuning.get_fret_mapping(chord_tone, chord_spec, scale, scale_key, scale_degree)
        print("we got mappingz of mapping {}".format(json.dumps(mappings)))
        last_3_notes = ((3, 9), (2, 7), (1, 6))
        self.tuning.get_pattern(mappings, self.pattern_config, last_3_notes, chord_type)


    def test_probable_pos(self):
        m = ((2,4), (2,7), (1,6))
        pos = self.tuning.get_probable_pos(m)
        self.assertEqual(pos, (1, 4))

        # reversing note order shouldn't affect the fret position
        # if all notes fit into a single position
        pos = self.tuning.get_probable_pos(list(reversed(m)))
        self.assertEqual(pos, (2, 4))

        # test super-positional jumps
        m = ((5, 3), (5, 8), (4, 12))
        pos = self.tuning.get_probable_pos(m)
        self.assertEqual(pos, (4, 8))

        # with super-positional jumps
        # reversing should change position
        pos = self.tuning.get_probable_pos(list(reversed(m)))
        self.assertEqual(pos, (5, 3))

    def test_get_roots(self):
        self.tuning.get_chord_roots()

