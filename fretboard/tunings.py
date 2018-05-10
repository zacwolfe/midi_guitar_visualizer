import math
import re
# Semitones from C to C D E F G A B
SEMITONES = [0, 2, 4, 5, 7, 9, 11]
# Chromatic melodic scale
CHROMATIC = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

LETTERS = 'CDEFGAB'
REGEX = r'^([a-gA-G])(#{1,4}|b{1,4}|x{1,2}|)(\d*)$'
p = re.compile(REGEX)

class Tuning(object):

    def __init__(self, num_frets):
        self.num_frets = num_frets
        self.num_strings = 6
        self.tuning = ['E4', 'B3', 'G3', 'D3', 'A2', 'E2']

    def get_num_strings(self):
        return self.num_strings

    def get_string_sci_pitch(self, string_num):
        return self.tuning[string_num]

    def get_string_midi_note(self, string_num):
        return to_midi(self.get_string_sci_pitch(string_num))

    # assumes midi channel == string number
    def get_string_and_fret(self, midi_note, channel):
        note = self.get_string_midi_note(channel)
        # print('midinote {} on chan {} converts to open string {} or {}'.format(midi_note, channel, note, from_midi(note)))
        return (channel, midi_note - note)

    def is_impossible_note(self, channel, midi_note):
        note = self.get_string_midi_note(channel)
        return midi_note < note or midi_note - note > self.num_frets


    def is_open_string(self, channel, midi_note):
        return self.get_string_midi_note(channel) == midi_note

    def get_distance(self, channel1, midi_note1, channel2, midi_note2):
        return abs(self.get_string_and_fret(midi_note1, channel1)[1] - self.get_string_and_fret(midi_note2, channel2)[1]) + abs(channel1 - channel2)

class StandardTuning(Tuning):
    pass

class P4Tuning(Tuning):
    def __init__(self, num_frets):
        super().__init__(num_frets)
        self.tuning = ['F4', 'C4', 'G3', 'D3', 'A2', 'E2']

def from_midi(midi):
  name = CHROMATIC[midi % 12]
  oct = int(math.floor(midi / 12) - 1)
  return '{}{}'.format(name, oct)

def to_midi (sci_pitch):
    p = parse_pitch(sci_pitch)
    if (not p[2] and p[2] != 0):
      return None
    return SEMITONES[p[0]] + p[1] + 12 * (p[2] + 1)

def parse_pitch(str):
    m = p.match(str)
    if not m:
      return None

    step = LETTERS.index(m.group(1).upper())
    alt = len(m.group(2).replace('x', '##'))
    if m.group(2) and m.group(2)[0] == 'b':
        alt *= -1
    oct = int(m.group(3)) if len(m.groups()) >= 3 else None
    return (step, alt, oct)


