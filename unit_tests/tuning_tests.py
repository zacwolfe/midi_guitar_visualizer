import unittest
from scales.scales import Scales, Chords, Patterns, chord_label_to_interval, parse_chord
from fretboard.tunings import StandardTuning, Tuning, P4Tuning
from fretboard.fretboard import get_fretboard_adv_defaults, get_fretboard_defaults, get_window_defaults, get_harmonic_definitions_defaults
from fretboard.pattern_mapper import P4TuningPatternMatcher
import json
from time import time
import cProfile
import pstats
from fretboard.midi import parse_metadata
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
        self.pattern_mapping = P4TuningPatternMatcher(self.tuning, self.chords_config, self.scale_config, self.pattern_config)

    def tearDown(self):

        pass

    def test_pattern(self):

        start = time()
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

        pattern_args = (chord_tone, chord_type, scale_name, scale_key, scale_degree)
        mappings = self.pattern_mapping.get_fret_mapping(*pattern_args)
        print("we got mappingz of mapping {}".format(json.dumps(mappings)))
        # last_3_notes = ((3, 9), (2, 7), (1, 6))
        # self.tuning.get_pattern(mappings, self.pattern_config, last_3_notes, chord_type)

        # last_3_notes = ((0, 6), (0, 9))
        last_3_notes = ((3, 5), (3, 9), (2, 7))
        mapping = self.pattern_mapping.get_pattern(pattern_args, self.pattern_config, last_3_notes, chord_type)
        end = time()
        print("We got the great pattern {}\n in {} millis".format(mapping, int(end*1000 - start*1000)))


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


    def test_pattern_mapping_perf_profiling(self):
        cProfile.runctx('self.pattern_mapping_perf_1()', globals(), locals())
        # self.pattern_mapping_perf_1()

    def pattern_mapping_perf_1(self):

        for n in range(0, 100000):
            chord = 'G#M7'
            scale_name = 'major'
            scale_key = 'G#'
            scale_degree = 0
            self._load_pattern(chord, scale_name, scale_key, scale_degree)

        # chord = 'Bbm7'
        # scale_name = 'major'
        # scale_key = 'G#'
        # scale_degree = 1
        # self._load_pattern(chord, scale_name, scale_key, scale_degree)


    def _load_pattern(self, chord, scale_name, scale_key, scale_degree):
        m = parse_chord(chord)
        if not m:
            return

        chord_tone = m[1]
        if m[2]:
            chord_tone += m[2]
        chord_type = m[3]

        pattern_args = (chord_tone, chord_type, scale_name, scale_key, scale_degree)
        mappings = self.pattern_mapping.get_fret_mapping(*pattern_args)
        last_3_notes = ((3, 10), (2, 8), (1, 7))
        self.pattern_mapping.get_pattern(pattern_args, last_3_notes, chord_type)

        return mappings



    def test_metadata_parse_perf(self):
        cProfile.runctx('self.parse_metadata_1()', globals(), locals())

    def parse_metadata_1(self):
        data = 'GM7#11 D_major(0)|21| '
        for n in range(0, 100000):
            parse_metadata(data)
