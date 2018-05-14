import argparse
from collections import defaultdict
# import constants
# from fretboard.tunings import P4Tuning, Tuning

import toml

def generate_chord_compatibilities(infile, outfile, chordfile):
    chords = toml.load(chordfile)['chords']
    scale_systems = toml.load(infile)

    systems = scale_systems.get('systems')
    scales = scale_systems.get('scales')

    for s in systems.values():
        s.sort()

    for name, scale in scales.items():
        s = sorted([int(sd) for sd in scale if not sd.strip().startswith('(')])
        systems[name] = s

    # print(toml.dumps(chords))
    for c in chords.values():
        c.sort()

    result = defaultdict(list)

    for chord_name,chord in chords.items():
        for scale_name, scale in systems.items():
            compatible_degrees = get_compatible_degrees(chord, scale)
            if compatible_degrees:
                result[scale_name].append({chord_name: compatible_degrees})


    # print(toml.dumps(result))

    with open(outfile, 'w') as f:
        toml.dump(result, f)

    # print(toml.dumps(toml.load(outfile)))


def get_compatible_degrees(chord, scale):
    degrees = []
    two_ocatave_scale = scale + [s + 12 for s in scale]
    for degree in range(12):
        if _is_sublist([scale_degree - degree for scale_degree in two_ocatave_scale], chord):
            degrees.append(degree)

    return degrees

# inefficient but simple
def _is_sublist(lst, sublst):
    return not set(sublst) - set(lst)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate chord compatibility file')
    parser.add_argument('-i','--input', type=str, help="scale spec input file")
    parser.add_argument('-o','--output', type=str, help="chord compatibility output file")
    parser.add_argument('-c','--chords', type=str, default='../chords.toml', help="chord definitions file")

    args = parser.parse_args()

    infile = args.input
    outfile = args.output
    chordfile = args.chords

    generate_chord_compatibilities(infile, outfile, chordfile)
