from .tunings import Tuning, CHROMATIC, NOTE_ACCIDENTAL_NORMALIZATION, parse_pitch, chord_label_to_interval, is_match
import functools
import math

class StandardTuningPatternMatcher(object):

    def __init__(self, tuning, chord_config, scale_config, pattern_config):
        self.chord_config = chord_config
        self.scale_config = scale_config
        self.pattern_config = pattern_config
        self.tuning = tuning
        pass

    @functools.lru_cache(maxsize=128)
    def get_fret_mapping(self, chord_key, chord_type, scale_name=None, scale_key=None, scale_degree=0):
        # print("cache miss on {}".format((chord_key, chord_type, scale_name, scale_key, scale_degree)))
        chord_def = self.chord_config.get_chord(chord_type)
        if not chord_def:
            raise ValueError("Chord type {} not found".format(chord_type))

        scale = None
        if scale_name:
            scale = self.scale_config.get_scale(scale_name)
        return self._get_fret_mapping(chord_key, chord_def, scale, scale_key, scale_degree)

    def _get_fret_mapping(self, chord_key, chord_def, scale=None, scale_key=None, scale_degree=0):

        if scale_degree == None:
            scale_degree = 0

        mapping = dict()
        # get num octaves to cover all possible notes and patterns
        num_octaves = int(math.ceil(self.tuning.num_frets / 12)) + 1

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

            scale_mapping_template = list(zip(scale, scale)) # make copy

            # extend scale thru all octaves
            for o in range(1, num_octaves):
                for f in scale:
                    scale_mapping_template.append((f + o * 12, f))
        else:
            scale_mapping_template = list()

        # normalize scale_key
        scale_key = NOTE_ACCIDENTAL_NORMALIZATION.get(scale_key, scale_key)

        for string_num in range(-2, self.tuning.num_strings + 2):
            scale_mapping = list(scale_mapping_template)
            chord_mappings = list(chord_mappings_template)
            # get open string root pitch
            sci_pitch = self.tuning.get_string_sci_pitch(string_num)
            m = parse_pitch(sci_pitch)
            if not m:
                raise ValueError("Illegal pitch {}".format(sci_pitch))

            # remove octave info
            string_key = m[3]

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
            chord_mappings = [(f[0] + chord_offset, f[1], f[2], None) for f in chord_mappings]
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
            chord_mappings = [(f[0] % 12, f[1], f[2], f[3]) for f in chord_mappings[splice_idx:]] + [f for f in chord_mappings if f[0] <= self.tuning.num_frets]
            # print("chord mappings after rewrap: {}".format(chord_mappings))

            if scale_mapping:
                # get fret scale_offset from open string of scale scale_key
                scale_offset = 0
                for idx in range(0, 12):
                    if CHROMATIC[(idx + key_idx) % 12] == scale_key:
                        scale_offset = idx

                # shift all notes up by scale_offset
                scale_mapping = [(f[0]+scale_offset,f[1]) for f in scale_mapping]

                # find notes to wrap around after shift
                splice_idx = len(scale_mapping)
                for i in range(len(scale_mapping), 0, -1):
                    if scale_mapping[i-1][0] < num_octaves * 12:
                        break
                    else:
                        splice_idx = i - 1

                # print("das slice is {} and frets is {}".format(splice_idx, frets))
                # prepend 'wrapped' notes to front
                scale_mapping = [(f[0] % 12, f[1]) for f in scale_mapping[splice_idx:]] + [f for f in scale_mapping if f[0] <= self.tuning.num_frets]
                # print("my scale_mapping is {}".format(scale_mapping))
                combined_mapping = list()

                curr_chord_idx = 0
                for sf, sd in scale_mapping:

                    found = False
                    for i in range(curr_chord_idx, len(chord_mappings)):
                        if chord_mappings[i][0] > sf:
                            break
                        else:
                            combined_mapping.append((chord_mappings[i][0],chord_mappings[i][1], chord_mappings[i][2], sd))
                            curr_chord_idx = i
                            if chord_mappings[i][0] == sf:
                                found = True
                                break

                    if not found:
                        combined_mapping.append((sf, None, None, sd))
                    else:
                        curr_chord_idx += 1

                # pick up any remaining chord mappings
                for i in range(curr_chord_idx, len(chord_mappings)):
                    combined_mapping.append((chord_mappings[i][0], chord_mappings[i][1], chord_mappings[i][2], None))

                chord_mappings = combined_mapping

            # fill up all the empty frets for quick index-based access
            # sparse_array = [None] * (self.num_frets + 1)
            # for m in chord_mappings:
            #     sparse_array[m[0]] = m
            #
            # mapping[string_num] = sparse_array
            mapping[string_num] = chord_mappings

        return mapping

    def get_pattern(self, pattern_mapping_args, last_notes, chord_type='default', scale_type='default'):
        pass



class P4TuningPatternMatcher(StandardTuningPatternMatcher):

    def __init__(self, tuning, chord_config, scale_config, pattern_config):
        super().__init__(tuning, chord_config, scale_config, pattern_config)

    @functools.lru_cache(maxsize=128)
    def get_pattern(self, pattern_mapping_args, last_notes, chord_type='default', scale_type='default'):
        # print("pat cache miss on {}".format((pattern_mapping_args, last_notes, chord_type, scale_type)))
        pattern_mapping = self.get_fret_mapping(*pattern_mapping_args)
        if not pattern_mapping:
            return None
        # avg_fret = get_average_fret(last_notes)
        matches = list()
        for note_tuple in last_notes:
            string_frets = pattern_mapping[note_tuple[0]]
            added = False
            for sf in string_frets:
                if not sf:
                    continue
                if sf[0] == note_tuple[1]:
                    matches.append((note_tuple[0], note_tuple[1], True, sf[1], sf[3]))
                    added = True

                elif sf[0] > note_tuple[1]:
                    break
            if not added:
                matches.append((note_tuple[0], note_tuple[1], False, None, None))

        # if the last note doesn't match or if no matches exist return None
        if not [m for m in matches if m[2]] or not matches[-1:][0][2]:
            return None

        arp_mode = True if len([n for n in matches if n[3]]) == len(matches) else False

        string_num, fret_pos = self.get_probable_pos(matches)

        mapping = None
        if arp_mode:
            # print("got matches {}".format(matches))
            roots = self.get_chord_roots(string_num, fret_pos, pattern_mapping, matches[len(matches) - 1])
            # print("got roots {}".format(roots))
            chord_patterns = self.pattern_config.get_default_arppeggio_patterns(self.tuning.get_name(), chord_type)
            # print("got chord patterns for {}:  {}".format(chord_type, chord_patterns))
            patterns = self.get_patterns(chord_patterns, pattern_mapping, roots)
            # print("got candidate patterns {}".format(patterns))
            pattern = self.choose_best_pattern(patterns, fret_pos, matches)
            # print("Got best pattern {}".format(pattern))
            if pattern:
                mapping = self.extend_pattern(pattern, chord_patterns, pattern_mapping)


        # else:
        #     roots = self.get_scale_roots(string_num, fret_pos, pattern_mapping, matches[len(matches) - 1])

        return mapping




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


    def get_chord_roots(self, string_num, fret_pos, pattern_mapping, last_match):
        # string_mapping = pattern_mapping[string_num]
        chord_degree = chord_label_to_interval(last_match[3])

        curr_fret = last_match[1]
        current_string = last_match[0]

        curr_root_fret = curr_fret - chord_degree

        lower_roots = list()

        while True:
            if current_string >= self.tuning.num_strings + 2:
                break

            if fret_pos - 1 <= curr_root_fret <= fret_pos + 4:
                lower_roots.append((current_string, curr_root_fret))
            elif curr_root_fret - fret_pos > 4:
                break

            current_string += 1
            curr_root_fret += 5

        curr_root_fret = curr_fret + (12 - chord_degree)
        current_string = last_match[0]
        upper_roots = list()

        while True:
            if current_string < -2:
                break

            if fret_pos - 1 <= curr_root_fret <= fret_pos + 4:
                upper_roots.append((current_string, curr_root_fret))
            elif curr_root_fret < fret_pos - 1:
                break

            current_string -= 1
            curr_root_fret -= 5

        return [lower_roots, upper_roots]

    def get_patterns(self, chord_patterns, pattern_mapping, roots):
        patterns = list()
        for string_num, fret_num in roots[0]:
            root_patterns = list()
            for pattern in chord_patterns:
                current_pattern = list()
                last_string = string_num
                last_fret = fret_num
                for relative_string, chord_tone in pattern:
                    snum = string_num+relative_string
                    if snum >= self.tuning.num_strings + 2 or snum < -2:
                        break
                    string_mapping = pattern_mapping[snum]

                    for n in string_mapping:
                        if not n:
                            continue
                        elif self.tuning.get_string_midi_note(last_string, last_fret) > self.tuning.get_string_midi_note(snum, n[0]):
                            continue
                        elif n[2] == chord_tone:
                            current_pattern.append((snum, n))
                            last_fret = n[0]
                            last_string = snum
                            break
                        # elif n[2] and n[2] > chord_tone:
                        #     break

                root_patterns.append(current_pattern)
                # print("the root_patt is {}".format(current_pattern))

            patterns.append(((string_num, fret_num), root_patterns))
        return patterns

    def get_string_midi_note_ext(self, string_num, fret_num):
        if string_num < self.tuning.num_strings and string_num > 0:
            return self.tuning.get_string_midi_note(string_num, fret_num)
        elif string_num < 0:
            return self.tuning.get_string_midi_note(0, fret_num) + abs(string_num)*5
        else:
            return self.tuning.get_string_midi_note(0, fret_num) - (string_num - self.tuning.num_strings + 1)*5

    def get_scale_roots(self, string_num, fret_pos, pattern_mapping, last_match):
        pass

    def choose_best_pattern(self, root_patterns, fret_pos, matches):
        results = list()

        for root, patterns in root_patterns:
            # print("For root {}".format(root))

            for position, pattern in enumerate(patterns):
                num_matches = 0
                total_frets = 0

                # print("pos #{}: {}".format(position + 1, pattern))
                for n in pattern:
                    total_frets += n[1][0]
                    if is_match(n, matches):
                        num_matches += 1


                results.append((num_matches, total_frets/len(pattern), position, pattern))

        results.sort(key = lambda n: (-n[0], abs(fret_pos - n[1])))

        # print("Fugging results for fret_pos {} are {}".format(fret_pos, results))

        return results[0][2], results[0][3] if results else None


    def extend_pattern(self, chosen_pattern, pattern_template, pattern_mapping):
        result = self.extend_down(chosen_pattern, pattern_template, pattern_mapping)
        # print("extended down we have {}".format(result))
        up = self.extend_up(chosen_pattern, pattern_template, pattern_mapping)
        # print("extended up we have {}".format(up))
        return result + [chosen_pattern] + up

    def extend_down(self, chosen_pattern, pattern_template, pattern_mapping):

        curr_position = chosen_pattern[0]
        start = chosen_pattern[1][0]
        s = (start[0], start[1][0])
        # print("starting down from {}".format(start))

        result = list()

        complete = False
        while not complete:

            curr_position = 2 if curr_position == 0 else curr_position - 1

            current_pattern = pattern_template[curr_position]
            current_pattern = list(reversed(current_pattern))
            offset = current_pattern[0][0]
            current_pattern = [[p[0] - offset, p[1]] for p in current_pattern]
            current_pattern.pop(0)  # remove root

            last_string = s[0]
            last_fret = s[1]
            # print('current pos {} and pattern {} and start {} and s {}'.format(curr_position, current_pattern, start, s))

            if last_string >= self.tuning.num_strings:
                complete = True
                continue

            pattern_result = list()
            for n in current_pattern:
                string_num = s[0] + n[0]
                if string_num >= self.tuning.num_strings:
                    complete = True
                    break
                string_mapping = pattern_mapping[string_num]
                if string_num != last_string:
                    last_fret = last_fret + 4
                    last_string = string_num
                sm = None

                for m in string_mapping:
                    if m[0] > last_fret:
                        break
                    if m[2] == n[1]:
                        sm = m


                if sm:
                    last_fret = sm[0]
                    pattern_result[0:0] = [(string_num, (sm[0], sm[1], sm[2], sm[3]))]

            if pattern_result:
                pattern_result = (curr_position, pattern_result)
                # print("got pattern_result {}".format(pattern_result))
                result[0:0] = [pattern_result]

            s = (last_string, last_fret)

        return result

    def extend_up(self, chosen_pattern, pattern_template, pattern_mapping):
        curr_position = chosen_pattern[0]
        start = chosen_pattern[1][-1]
        s = (start[0], start[1][0])

        result = list()

        complete = False
        while not complete:

            curr_position = 0 if curr_position == 2 else curr_position + 1

            current_pattern = list(pattern_template[curr_position])
            # current_pattern = list(reversed(current_pattern))
            # offset = current_pattern[0][0]
            # current_pattern = [[p[0] - offset, p[1]] for p in current_pattern]
            current_pattern.pop(0)  # remove last root

            last_string = s[0]
            last_fret = s[1]
            # print('current pos {} and pattern {} and start {} and s {}'.format(curr_position, current_pattern, start, s))

            if last_string < 0:
                complete = True
                continue

            pattern_result = list()
            for n in current_pattern:
                string_num = s[0] + n[0]
                if string_num < 0:
                    complete = True
                    break
                string_mapping = pattern_mapping[string_num]
                if string_num != last_string:
                    last_fret = max(0, last_fret - 4)
                    last_string = string_num
                sm = None
                for m in string_mapping:
                    if m[0] < last_fret:
                        continue
                    elif m[2] == n[1]:
                        sm = m
                        last_fret = sm[0]
                        break

                if sm:
                    pattern_result.append((string_num, (sm[0], sm[1], sm[2], sm[3])))

            if pattern_result:
                pattern_result = (curr_position, pattern_result)
                # print("got ascending pattern_result {}".format(pattern_result))
                result.append(pattern_result)

            s = (last_string, last_fret)

        return result

