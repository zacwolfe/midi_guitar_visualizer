import math
import re
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

    def get_fret_mapping(self, chord_key, chord_def, scale=None, scale_key=None, scale_degree=0):

        # get num octaves to cover all possible notes
        num_octaves = int(math.ceil(self.num_frets / 12))

        chord_mappings_template = list(chord_def)
        # extend scale thru all octaves
        for o in range(1, num_octaves):
            for f in chord_def:
                chord_mappings_template.append((f[0] + o * 12, f[1], f[2]))

        # normalize chord_key
        chord_key = NOTE_ACCIDENTAL_NORMALIZATION.get(chord_key, chord_key)

        if scale:
            if scale_degree > 0:
                shift_down = scale[scale_degree]
                scale = [d - shift_down for d in scale[scale_degree:]] + [d + 12 - shift_down for d in scale[0:scale_degree]]

            scale_mapping_template = list(scale) # make copy

            # extend scale thru all octaves
            for o in range(1, num_octaves):
                for f in scale:
                    scale_mapping_template.append(f + o * 12)
        else:
            scale_mapping_template = dict()

        # normalize scale_key
        scale_key = NOTE_ACCIDENTAL_NORMALIZATION.get(scale_key, scale_key)

        mapping = dict()

        for string_num in range(0, self.num_strings):
            scale_mapping = list(scale_mapping_template)
            chord_mappings = list(chord_mappings_template)
            # get open string root pitch
            sci_pitch = self.get_string_sci_pitch(string_num)
            m = pitch_pattern.match(sci_pitch)
            if not m:
                raise ValueError("Illegal pitch {}".format(sci_pitch))

            # remove octave info
            string_key = m.group(1) + m.group(2)

            # normalize string note identifiers
            string_key = NOTE_ACCIDENTAL_NORMALIZATION.get(string_key, string_key)

            # get index of open string note in chromatic scale
            key_idx = 0
            for idx, val in enumerate(CHROMATIC):
                if val == string_key:
                    key_idx = idx
                    break

            # get fret scale_offset from open string of scale scale_key
            chord_offset = 0
            for idx in range(0, 12):
                if CHROMATIC[(idx + key_idx) % 12] == chord_key:
                    chord_offset = idx
                    break

            # shift all notes up by scale_offset
            chord_mappings = [(f[0] + chord_offset, f[1], f[2]) for f in chord_mappings]
            # print("chord mappings before rewrap: {}".format(chord_mappings))

            # find notes to wrap around after shift
            splice_idx = len(chord_mappings)
            for i in range(len(chord_mappings), 0, -1):
                if chord_mappings[i - 1][0] < num_octaves * 12:
                    break
                else:
                    splice_idx = i - 1

            # print("das slice is {} and frets is {}".format(splice_idx, frets))
            # prepend 'wrapped' notes to front
            chord_mappings = [(f[0] % 12, f[1], f[2]) for f in chord_mappings[splice_idx:]] + [f for f in chord_mappings if f[0] <= self.num_frets]
            # print("chord mappings after rewrap: {}".format(chord_mappings))

            if scale_mapping:
                # get fret scale_offset from open string of scale scale_key
                scale_offset = 0
                for idx in range(0, 12):
                    if CHROMATIC[(idx + key_idx) % 12] == scale_key:
                        scale_offset = idx

                # shift all notes up by scale_offset
                scale_mapping = [f+scale_offset for f in scale_mapping]

                # find notes to wrap around after shift
                splice_idx = len(scale_mapping)
                for i in range(len(scale_mapping), 0, -1):
                    if scale_mapping[i-1] < num_octaves * 12:
                        break
                    else:
                        splice_idx = i - 1

                # print("das slice is {} and frets is {}".format(splice_idx, frets))
                # prepend 'wrapped' notes to front
                scale_mapping = [f % 12 for f in scale_mapping[splice_idx:]] + [f for f in scale_mapping if f <= self.num_frets]

                combined_mapping = list()

                curr_chord_idx = 0
                for sd in scale_mapping:

                    found = False
                    for i in range(curr_chord_idx, len(chord_mappings)):
                        if chord_mappings[i][0] > sd:
                            break
                        else:
                            combined_mapping.append(chord_mappings[i])
                            curr_chord_idx = i
                            if chord_mappings[i][0] == sd:
                                found = True
                                break

                    if not found:
                        combined_mapping.append((sd, None, None))
                    else:
                        curr_chord_idx += 1

                # pick up any remaining chord mappings
                for i in range(curr_chord_idx, len(chord_mappings)):
                    combined_mapping.append(chord_mappings[i])

                chord_mappings = combined_mapping

            mapping[string_num] = chord_mappings

        return mapping


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
    m = pitch_pattern.match(str)
    if not m:
      return None

    step = LETTERS.index(m.group(1).upper())
    alt = len(m.group(2).replace('x', '##'))
    if m.group(2) and m.group(2)[0] == 'b':
        alt *= -1
    oct = int(m.group(3)) if len(m.groups()) >= 3 else None
    return (step, alt, oct)


