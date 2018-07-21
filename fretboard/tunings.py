import math
import re
from statistics import mean
from scales.scales import chord_label_to_interval
import functools
# Semitones from C to C D E F G A B
SEMITONES = [0, 2, 4, 5, 7, 9, 11]
# Chromatic melodic scale
CHROMATIC = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
NOTE_ACCIDENTAL_NORMALIZATION = {'C#':'Db','D#':'Eb', 'F#':'Gb', 'G#':'Ab', 'A#':'Bb'}

LETTERS = 'CDEFGAB'
PITCH_REGEX = r'^([a-gA-G])(#{1,4}|b{1,4}|x{1,2}|)(\d*)$'
pitch_pattern = re.compile(PITCH_REGEX)

class Tuning(object):

    def __init__(self, num_frets):
        self.num_frets = num_frets
        self.num_strings = 6
        self.tuning = ['E4', 'B3', 'G3', 'D3', 'A2', 'E2']
        self.extended_tuning = ['D5', 'A4', 'E4', 'B3', 'G3', 'D3', 'A2', 'E2', 'B1', 'F1']

    def get_name(self):
        return None

    def get_num_strings(self):
        return self.num_strings

    def get_string_sci_pitch(self, string_num):
        return self.extended_tuning[string_num + 2]

    @functools.lru_cache(maxsize=256)
    def get_string_midi_note(self, string_num, fret_num):
        # print("cache miss note on {}".format((string_num, fret_num)))
        return to_midi(self.get_string_sci_pitch(string_num)) + fret_num

    # assumes midi channel == string number
    def get_string_and_fret(self, midi_note, channel):
        note = self.get_string_midi_note(channel, 0)
        # print('midinote {} on chan {} converts to open string {} or {}'.format(midi_note, channel, note, from_midi(note)))
        return (channel, midi_note - note)

    def is_impossible_note(self, channel, midi_note):
        try:
            note = self.get_string_midi_note(channel, 0)
            return midi_note < note or midi_note - note > self.num_frets
        except IndexError:
            return True

    def is_open_string(self, channel, midi_note):
        return self.get_string_midi_note(channel, 0) == midi_note

    def get_distance(self, channel1, midi_note1, channel2, midi_note2):
        return abs(self.get_string_and_fret(midi_note1, channel1)[1] - self.get_string_and_fret(midi_note2, channel2)[1]) + abs(channel1 - channel2)



class StandardTuning(Tuning):

    def get_name(self):
        return 'standard'

class P4Tuning(Tuning):
    def __init__(self, num_frets):
        super().__init__(num_frets)
        self.tuning = ['F4', 'C4', 'G3', 'D3', 'A2', 'E2']
        self.extended_tuning = ['Eb5', 'Bb4', 'F4', 'C4', 'G3', 'D3', 'A2', 'E2', 'B1', 'F1']

    def get_name(self):
        return 'p4'


    def get_probable_pos(self, matches):

        curr_pos = -1

        for m in matches:
            fret = m[1]
            if curr_pos < 0:
                curr_pos = fret
            elif fret - curr_pos > 4:
                curr_pos = fret - 4
            elif fret < curr_pos:
                curr_pos = fret

        return (matches[len(matches) - 1][0], curr_pos)


def is_match(n, matches):
    for m in matches:
        if n[0] == m[0] and n[1][0] == m[1]:
            return True

    return False

def from_midi(midi):
  name = CHROMATIC[midi % 12]
  oct = int(math.floor(midi / 12) - 1)
  return '{}{}'.format(name, oct)

def to_midi (sci_pitch):
    p = parse_pitch(sci_pitch)
    if not p:
        return None
    if (not p[2] and p[2] != 0):
      return None
    return SEMITONES[p[0]] + p[1] + 12 * (p[2] + 1)


@functools.lru_cache(maxsize=128)
def parse_pitch(s):
    m = pitch_pattern.match(s)
    if not m:
        return None

    key = m.group(1).upper()
    step = LETTERS.index(key)
    accidental = m.group(2).replace('x', '##')
    alt = len(accidental)
    if m.group(2) and m.group(2)[0] == 'b':
        alt *= -1
    oct = int(m.group(3)) if len(m.groups()) >= 3 else None
    result = (step, alt, oct, key + accidental)
    return result

def get_average_fret(string_fret_tuples):
    return mean([f[1] for f in string_fret_tuples])
