from kivy.clock import mainthread
from .utils import mainthread_interrupt
from constants import current_time_millis
from scales.scales import parse_chord
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.config import ConfigParser
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import BooleanProperty
from kivy.animation import Animation
import kivy.utils as utils
from kivy.properties import ConfigParserProperty
from kivy.clock import Clock
import collections



def get_fretboard_adv_defaults():
    return {
        'fretboard_outline_width': 5,
        'fret_thickness_ratio': 0.002,
        'string_box_width': 50,
        'string_box_line_width': 3,
        'string_activation_width': 30,
        'string_activation_height': 30,
        'nut_line_width': 3,
        'nut_slot_width': 3,
        'string_inset_ratio': .07,
        'dot_width_ratio': 0.015,
        'dot_height_ratio': 0.015,
        'finger_offset_ratio': 0.2,
        'finger_width_ratio': 0.02,
        'note_expiration': 0.5,
        'mma_script_loc': './mma/mma.py',
        'mma_tmp_dir': './mma/tmp',
    }

def get_fretboard_defaults():
    return {
        'neck_taper': .08,
        'margin_size': 10,
        'num_frets': 22,
        'fret_color': utils.get_hex_from_color((0.3, 0.3, 0.3, 0.5)),
        'string_activation_color': utils.get_hex_from_color((0.0, 1.0, 0.0, 1.0)),
        'nut_width_ratio': .01,
        'nut_color': utils.get_hex_from_color((.902, .541, 0.0, 0.5)),
        'finger_color': utils.get_hex_from_color((0.1, 0.1, 1.0, 0.8)),
        'show_tracers': 1,
        'note_fade_time': 0.0,
        'tracer_fade_time': 0.5,
        'tracer_line_ratio': 0.01,
    }

def get_window_defaults():
    return {
        'initial_width': 1800,
        'initial_screen_loc_x': 50,
        'initial_screen_loc_y': 400,
        'height_ratio': .36,
    }

def get_harmonic_definitions_defaults():
    return {
        'scale_system_file': '../scale_systems.toml',
        'chords_file': '../chords.toml',
        'patterns_file': '../patterns.toml',
    }



class Fretboard(RelativeLayout):

    # need special setting item for these
    string_guage_range = [14, 45]
    fret_dot_locations = [3, 5, 7, 9, 12, 15, 17, 19, 21]

    neck_taper = ConfigParserProperty(0.0, 'fretboard', 'neck_taper', 'app', val_type=float)
    fretboard_outline_width = ConfigParserProperty(0, 'fretboard_adv', 'fretboard_outline_width', 'app', val_type=int)
    fret_thickness_ratio = ConfigParserProperty(0.0, 'fretboard_adv', 'fret_thickness_ratio', 'app', val_type=float)
    margin_size = ConfigParserProperty(0, 'fretboard', 'margin_size', 'app', val_type=int)
    num_frets = ConfigParserProperty(0, 'fretboard', 'num_frets', 'app', val_type=int)
    fret_color = (0.3, 0.3, 0.3, 0.5)

    # fret_color = utils.get_color_from_hex(ConfigParserProperty(0, 'fretboard', 'fret_color', 'app'))

    string_box_width = ConfigParserProperty(0.0, 'fretboard_adv', 'string_box_width', 'app', val_type=int)
    string_box_line_width = ConfigParserProperty(0.0, 'fretboard_adv', 'string_box_line_width', 'app', val_type=int)
    string_activation_width = ConfigParserProperty(0.0, 'fretboard_adv', 'string_activation_width', 'app', val_type=int)
    string_activation_height = ConfigParserProperty(0.0, 'fretboard_adv', 'string_activation_height', 'app', val_type=int)
    string_activation_color = (0.0, 1.0, 0.0, 1.0)


    nut_width_ratio = ConfigParserProperty(0.0, 'fretboard', 'nut_width_ratio', 'app', val_type=float)
    nut_line_width = ConfigParserProperty(0.0, 'fretboard_adv', 'nut_line_width', 'app', val_type=int)
    nut_color = (.902, .541, 0.0, 0.5)
    nut_slot_width = ConfigParserProperty(0.0, 'fretboard_adv', 'nut_slot_width', 'app', val_type=int)

    string_inset_ratio = ConfigParserProperty(0.0, 'fretboard_adv', 'string_inset_ratio', 'app', val_type=float)

    dot_width_ratio = ConfigParserProperty(0.0, 'fretboard_adv', 'dot_width_ratio', 'app', val_type=float)
    dot_height_ratio = ConfigParserProperty(0.0, 'fretboard_adv', 'dot_height_ratio', 'app', val_type=float)

    finger_offset_ratio = ConfigParserProperty(0.0, 'fretboard_adv', 'finger_offset_ratio', 'app', val_type=float)
    finger_width_ratio = ConfigParserProperty(0.0, 'fretboard_adv', 'finger_width_ratio', 'app', val_type=float)
    finger_color = (0.1, 0.1, 1.0, 0.8)

    show_tracers = ConfigParserProperty(1, 'fretboard', 'show_tracers', 'app', val_type=int)
    note_fade_time = ConfigParserProperty(0.0, 'fretboard', 'note_fade_time', 'app', val_type=float)
    note_expiration = ConfigParserProperty(0.0, 'fretboard_adv', 'note_expiration', 'app', val_type=float)
    tracer_fade_time = ConfigParserProperty(0.0, 'fretboard', 'tracer_fade_time', 'app', val_type=float)
    tracer_line_ratio = ConfigParserProperty(0.0, 'fretboard', 'tracer_line_ratio', 'app', val_type=float)




    # Config.set('graphics', 'width', str(initial_width))
    # Config.set('graphics', 'height', str(int(initial_width * height_ratio)))
    # Config.set('graphics', 'position', 'custom')
    # Config.set('graphics', 'left', 100)
    # Config.set('graphics', 'top', 10)
    current_harmonic_mapping = None
    current_harmonic_mapping_cachekey = None
    current_pattern_mapping = None
    current_harmonic_settings = None
    last_note = None
    current_chord_type = None
    scales_visible = BooleanProperty(True)
    chord_tones_visible = BooleanProperty(True)
    common_chord_tones_visible = True
    tracking_patterns = True

    note_queue = collections.deque(maxlen=3)
    def __init__(self, tuning, pattern_mapper, **kwargs):
        super(Fretboard, self).__init__(**kwargs)

        def get_color(key):
            return utils.get_color_from_hex(ConfigParser.get_configparser('app').get('fretboard',key))

        print('fretcolor is {}'.format(get_color('fret_color')))

        self.fret_color = get_color('fret_color')
        self.string_activation_color = get_color('string_activation_color')
        self.nut_color = get_color('nut_color')
        self.finger_color = get_color('finger_color')
        self.tuning = tuning
        self.pattern_mapper = pattern_mapper
        self.notes = {}
        self.scale_notes = {}

        with self.canvas:
            print("WITH SHITTING...")
            # Window.size = (self.initial_width, self.initial_width * self.height_ratio + self.margin_size * 2)
            # Window.left = self.initial_screen_loc_x
            # Window.top = self.initial_screen_loc_y
            Window.clearcolor = (1, 1, 1, 1)
            Color(1,1,1,1, group='fb')
            self.rect = Rectangle(pos=self.pos, size=self.size, group='fb')

            pass

        with self.canvas.before:

        # you can use this to add instructions rendered before
            print("BEFORE...")
            # self.draw_fretboard()
            self.redraw_fretboard()
            pass

        with self.canvas.after:
            print("AFTER...")
            # self.redraw_fretboard()
            pass

        self.bind(size=self.redraw_fretboard)
        self.bind(scales_visible=self.update_scale_visibility)
        self.bind(chord_tones_visible=self.update_chord_tones_visibility)
        # self.bind(pos=self.redraw_fretboard)

    # def on_touch_down(self, touch):
    #     pass
        # with self.canvas:
            # Color(1, 1, 0)
            # d = 30.
            # Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            # print("touch! {},{}".format(touch.x, touch.y))
            # self.show_finger(touch.x, touch.y)

    def get_fretboard_outline(self):
        with self.canvas:
            hite = self.fretboard_height()
            taper_amt = hite*self.neck_taper*0.5
            return (self.width - self.margin_size, self.margin_size,
             self.margin_size, self.margin_size + taper_amt,
             self.margin_size, self.margin_size+taper_amt+(hite - 2*taper_amt),
             self.width - self.margin_size, self.margin_size + hite,
             self.width - self.margin_size, self.margin_size)
            # return (10, 15, self.width - 10, 10, self.width - 10, self.height - 20, 10, self.height - 35, 10, 15)

    def draw_string_box(self):
        hite = self.fretboard_height()
        taper_amt = hite * self.neck_taper * 0.5
        points =  (self.width - (self.margin_size + self.string_box_width), self.margin_size + ((self.string_box_width / self.neck_length()) * taper_amt),
                   self.width - (self.margin_size + self.string_box_width), self.margin_size + hite - ((self.string_box_width / self.neck_length()) * taper_amt))
        Color(0, 0, 0, group='fb')
        Line(points=points, width=self.string_box_line_width, cap='round', group='fb')

    def neck_length(self):
        return (self.width - 2 * self.margin_size)

    def fretboard_height(self):
        # return self.neck_length() * self.height_ratio
        return self.height - 2*self.margin_size

    def fretboard_length(self):
        return self.neck_length() - (self.string_box_width + self.nut_width())

    def draw_nut(self):
        max_fretboard_height = self.fretboard_height()
        taper_amt = max_fretboard_height * self.neck_taper * 0.5
        neck_len = self.neck_length()
        nut_width = self.nut_width(neck_len=neck_len)
        relative_taper_amt = ((neck_len - nut_width) / neck_len) * taper_amt
        points = (self.margin_size + nut_width,
                  self.margin_size + relative_taper_amt,
                  self.margin_size + nut_width,
                  self.margin_size + max_fretboard_height - relative_taper_amt)
        Color(0, 0, 0, group='fb')
        Line(points=points, width=self.string_box_line_width, cap='round', group='fb')
        Color(*self.nut_color, group='fb')
        Rectangle(pos=(self.margin_size, self.margin_size + relative_taper_amt), size=(nut_width, max_fretboard_height - relative_taper_amt*2), group='fb')
        self.draw_nut_string_slots()

    def draw_nut_string_slots(self):

        nut_width = self.nut_width()
        start_x = self.margin_size
        end_x = start_x + nut_width
        Color(0, 0, 0, group='fb')
        for offset in self.get_string_locations(0):
            Line(points=(start_x, self.margin_size + offset, end_x, self.margin_size + offset), width=self.nut_slot_width, cap='round', group='fb')

    def draw_strings(self):

        nut_width = self.nut_width()
        start_x = self.margin_size + nut_width
        end_x = self.width - (self.margin_size + self.string_box_width)
        start_offsets = self.get_string_locations(0)
        end_offsets = self.get_string_locations(self.fretboard_length())
        Color(0, 0, 0, group='fb')
        string_guage_width_ratio = .00035
        max_fretboard_height = self.fretboard_height()
        guage_step = (abs(self.string_guage_range[0] - self.string_guage_range[1])/self.tuning.get_num_strings()) * string_guage_width_ratio*max_fretboard_height
        for string_num in range(0, self.tuning.get_num_strings()):
            string_width = self.string_guage_range[0]*string_guage_width_ratio*max_fretboard_height + guage_step*string_num
            print('string {} has width {}'.format(string_num+1, string_width))
            Line(points=(self.margin_size, self.margin_size + start_offsets[string_num], start_x, self.margin_size + start_offsets[string_num],
                         end_x, self.margin_size + end_offsets[string_num]), width=min(10, max(string_width, 1)), cap='none', group='fb')


    def nut_width(self, neck_len=None):
        if neck_len is None:
            neck_len = self.neck_length()

        return self.nut_width_ratio * neck_len


    def draw_frets(self):
        hite = self.fretboard_height()
        taper_amt = hite * self.neck_taper * 0.5
        neck_len = self.neck_length()
        nut_width = self.nut_width(neck_len=neck_len)
        dot_width = neck_len * self.dot_width_ratio
        dot_height = neck_len * self.dot_height_ratio
        fret_thickness = neck_len*self.fret_thickness_ratio

        last_x = 0
        for fret_num in range(1, self.num_frets):
            fret_x = self.get_fret_x(fret_num)
            relative_taper_amt = ((neck_len - (nut_width + fret_x)) / neck_len) * taper_amt # adjust for line cap
            start_y = self.margin_size+relative_taper_amt
            end_y = self.margin_size+hite-relative_taper_amt
            points = (fret_x, start_y, fret_x, end_y)
            Color(*self.fret_color, group='fb')
            Line(points=points, width=fret_thickness, group='fb', cap='none')
            Color(0, 0, 0, group='fb')
            if fret_num in self.fret_dot_locations:
                center_x = last_x + (fret_x - last_x)*.5 - dot_width*0.5
                if fret_num != 12:
                    center_y = self.margin_size + hite*0.5 - dot_height*.5
                    Ellipse(pos=(center_x, center_y), size=(dot_width, dot_height), group='fb')
                else:
                    # some fudge allowed here
                    center_y = self.margin_size + hite * 0.333 - dot_height * .5
                    Ellipse(pos=(center_x, center_y), size=(dot_width, dot_height), group='fb')

                    center_y = self.margin_size + hite * 0.666 - dot_height * .5
                    Ellipse(pos=(center_x, center_y), size=(dot_width, dot_height), group='fb')

            last_x = fret_x


    def get_finger_location(self, string_num, fret_num):
        fret_x = self.get_fret_x(fret_num)
        prev_fret_x = self.get_fret_x(fret_num - 1)

        finger_width = self.width*self.finger_width_ratio
        pos_x = fret_x - (fret_x - prev_fret_x)*self.finger_offset_ratio
        pos_y = self.get_string_locations(pos_x)[string_num] + self.margin_size
        if pos_x + finger_width*0.5 > fret_x:
            pos_x = fret_x - finger_width*0.5

        return (pos_x, pos_y)

    def track_patterns(self, track):
        self.tracking_patterns = track

    def midi_note_on(self, midi_note, channel, time=None):
        self.note_on(*self.tuning.get_string_and_fret(midi_note, channel), time)


    def midi_note_off(self, midi_note, channel):
        self.note_off(*self.tuning.get_string_and_fret(midi_note, channel))

    # @mainthread_interrupt
    def note_on(self, string_num, fret_num, time=None):
        self.note_queue.append((string_num, fret_num, time))
        if self.tracking_patterns:
            self.update_pattern()

        note_id = self.add_tone_marker(string_num, fret_num, None, None, None, True)
        # note_id = _generate_note_id(string_num, fret_num)
        #
        # note = self.notes.get(note_id)
        # if note:
        #     note.show()
        # else:
        #
        #
        #     loc = self.get_finger_location(string_num, fret_num)
        #
        #     pos_hint = {'center_x': loc[0]/self.width, 'center_y': loc[1]/self.height}
        #     size_hint = (self.finger_width_ratio, (self.finger_width_ratio * self.width / self.height))
        #     # print('pos_hint is {}'.format(pos_hint))
        #
        #     note = Note(self, string_num, fret_num, self.note_fade_time, pos_hint=pos_hint, size_hint=size_hint)
        #     self.notes[note_id] = note
        #     self.add_widget(note)


        if self.show_tracers:
            note = self.scale_notes[note_id]
            curr_time = current_time_millis()

            if self.last_note and self.last_note[0] != note and curr_time - self.last_note[1] < self.note_expiration*1000:
                tracer_line_thickness = self.tracer_line_ratio*self.width
                tracer = Tracer(self, self.last_note[0].string_num,self.last_note[0].fret_num , note.string_num, note.fret_num, self.tracer_fade_time, tracer_line_thickness)
                self.add_widget(tracer)

            self.last_note = (note, curr_time)

    # @mainthread_interrupt
    def note_off(self, string_num, fret_num):
        # note_id = _generate_note_id(string_num, fret_num)
        note_id = _generate_scale_note_id(string_num, fret_num)
        note = self.scale_notes.get(note_id)
        # note = self.notes.get(note_id)
        if note:
            note.set_being_played(False)
            # Animation.cancel_all(note.color, 'a')
            # Animation(a=0, duration=1, on_complete=self.hide_note)
            # note.hidden = True
            # return

        # note = self.notes.pop(note_id, None)
        # if note:
        #     self.remove_widget(note)

    def update_note(self, note):
        loc = self.get_finger_location(note.string_num, note.fret_num)
        pos_hint = {'center_x': loc[0] / self.width, 'center_y': loc[1] / self.height}
        size_hint = (self.finger_width_ratio, (self.finger_width_ratio * self.width / self.height))
        note.pos_hint = pos_hint
        note.size_hint = size_hint

    def get_tracer_points(self, tracer):
        loc_start = self.get_finger_location(tracer.string_start, tracer.fret_start)
        loc_end = self.get_finger_location(tracer.string_end, tracer.fret_end)
        return loc_start + loc_end


    def draw_notes(self):
        pass
        # notelist = list(self.notes.values())
        # print("notes is {} w/len {}".format(self.notes, len(notelist)))
        # for note in notelist:
        #     self.remove_widget(note)
        #     self.notes.pop(note.id, None)
        #     print('popped {}'.format(note.id))
        #     self.note_on(note.string_num, note.fret_num)

    def draw_string_activation(self, string_num):
        offset = self.get_string_locations(self.fretboard_length())[string_num]
        Color(*self.string_activation_color, group='fb')
        pos_x = self.width - (self.margin_size + self.string_box_width) + 10
        Ellipse(pos=(pos_x, offset - self.string_activation_height*0.5 + self.margin_size), size=(self.string_activation_width, self.string_activation_height), group='fb')


    # def show_finger(self, x_pos, y_pos):

    def get_string_locations(self, dist_from_nut):
        hite = self.fretboard_height()

        inset_hight = hite * self.string_inset_ratio
        string_span = hite - inset_hight * 2
        string_spacing = string_span/(self.tuning.get_num_strings() - 1)

        taper_amt = hite * self.neck_taper * 0.5
        neck_len = self.neck_length()
        nut_width = self.nut_width(neck_len=neck_len)

        relative_taper_amt = ((neck_len - (nut_width + dist_from_nut)) / neck_len) * taper_amt
        board_height_pct = (hite - relative_taper_amt*2)/hite
        return [relative_taper_amt + board_height_pct*(inset_hight + (x*string_spacing)) for x in reversed(range(0, self.tuning.get_num_strings()))]


    def get_fret_x(self, fret_num):
        return self.get_fret_dist_from_nut(fret_num) + self.margin_size + self.nut_width()


    def get_fret_dist_from_nut(self, fret_num):
        return self.fretboard_length() * self.get_normalized_fret_dist_to_nut(fret_num)


    def redraw_fretboard(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

        with self.canvas:
            print("redrawing {}".format(self.get_fretboard_outline()))
            # self.canvas.get_group('fb')
            self.canvas.remove_group('fb')
            # self.canvas.clear()
            self.draw_fretboard()

    def draw_fretboard(self):
        Color(0, 0, 0, group='fb')
        print("my rect is pos: {} size: {}".format(self.rect.pos, self.rect.size))
        Line(points=self.get_fretboard_outline(), width=self.fretboard_outline_width, cap='round', joint='round', group='fb')
        self.draw_string_box()
        self.draw_nut()
        self.draw_frets()
        self.draw_strings()
        self.draw_notes()


    def get_normalized_fret_dist_to_nut(self, fret_num):
        if fret_num <= 0:
            return 0.0

        s = 1.0
        return _dist_from_nut(s, fret_num)/_dist_from_nut(s, self.num_frets)

    def extract_notes(self, pattern_mapping):
        return [(n[0], n[1][0]) for n in [seq for p in pattern_mapping for seq in p[1]]]

    def update_pattern(self):
        if self.current_harmonic_mapping and self.current_chord_type:
            recent_notes = self.get_recent_notes()

            if not recent_notes:
                return

            curr_patt_notes = self.extract_notes(self.current_pattern_mapping) if self.current_pattern_mapping else []

            if curr_patt_notes and self.does_pattern_match(curr_patt_notes, recent_notes):
                # print("pattern is still relevant, continuing...")
                return

            new_pattern_mapping = self.pattern_mapper.get_pattern(self.current_harmonic_mapping_cachekey, recent_notes, self.current_chord_type)

            if new_pattern_mapping:

                new_notes = self.extract_notes(new_pattern_mapping)
                if curr_patt_notes:
                    old = set(curr_patt_notes)
                    new = set(new_notes)
                    to_hide = old - new
                    to_add = new - old
                    if not to_hide and not to_add:
                        # nothing to do
                        # print("same damn thing all over again!!!")
                        return

                    self.hide_pattern(to_hide)
                    new_notes = to_add

                self.current_pattern_mapping = new_pattern_mapping
                self.show_pattern(new_notes)

                # print("Updating: We got the grand pattern {}".format(self.current_pattern_mapping))

    def get_recent_notes(self):
        current_time = current_time_millis()
        max_delay = 1500

        last_time = None
        result = collections.deque()
        for n in reversed(self.note_queue):
            if (not last_time and current_time - n[2] < max_delay) or (n[2] - last_time < max_delay):
                last_time = n[2]
                result.appendleft((n[0], n[1]))
            else:
                break

        return tuple(result)

    def does_pattern_match(self, pattern, recent_notes):
        return recent_notes[-1] in pattern


    def add_some_stuff(self):
        # self.show_chord_tones('G7b9', 'harmonic_minor', 'G', 4)
        # self.show_chord_tones('G7b9b13', 'melodic_minor', 6, 'G')
        # self.note_on(0, 1)
        # self.note_on(1, 11)
        # self.note_on(2, 12)
        # self.note_on(5, 5)
        # self.note_on(5, 1)
        # self.note_on(4, 22)
        #
        # self.draw_string_activation(2)
        pass

    def add_some_more_stuff(self):
        # time = current_time_millis()
        # self.note_on(5,3, time)
        # self.note_on(5,4, time)

        # self.show_chord_tones('G#M7', 'major', 'G#', 0)
        pass

    def remove_some_stuff(self):
        pass
        # self.note_off(0,1)
        # self.note_off(1, 11)
        # self.note_off(2, 12)
        # self.draw_finger_location(1, 0)
        # self.draw_finger_location(11, 1)
        # self.draw_finger_location(12, 2)
        # self.draw_finger_location(5, 5)
        # self.draw_finger_location(22, 4)
        #
        # self.draw_string_activation(2)

    def show_pattern(self, notes):
        for n in notes:
            self.highlight_tone_marker(*n)

    def hide_pattern(self, notes):
        for n in notes:
            self.highlight_tone_marker(*n, hide=True)


    def show_chord_tones(self, chord, scale_name=None, scale_key=None, scale_degree=None):
        m = parse_chord(chord)
        if not m:
            return


        harmonic_setting = (chord, scale_name, scale_key, scale_degree)
        if self.current_harmonic_settings == harmonic_setting:
            return

        else:
            self.current_harmonic_settings = harmonic_setting

        chord_tone = m[1]
        if m[2]:
            chord_tone += m[2]
        chord_type = m[3]

        self.current_harmonic_mapping_cachekey = (chord_tone, chord_type, scale_name, scale_key, scale_degree)

        mappings = self.pattern_mapper.get_fret_mapping(*self.current_harmonic_mapping_cachekey)
        # mappings = self.tuning.get_fret_mapping(chord_tone, chord_spec, scale, scale_key, scale_degree)
        self.current_harmonic_mapping = mappings
        # self.current_harmonic_mapping_cachekey = (chord_tone, str(chord_spec) if chord_spec else None, str(scale) if scale else None, scale_key, 0 if scale_degree is None else scale_degree)
        self.current_chord_type = chord_type
        # print("we got strong mappingz of mapping {}".format(mappings))

        visible_notes = set()

        for string_num, frets in mappings.items():
            if string_num >= self.tuning.num_strings or string_num < 0:
                continue
            for mapping in frets:
                if mapping:
                    visible_notes.add(self.add_tone_marker(string_num, mapping[0], mapping[1], mapping[2], mapping[3]))

        # hide non-visible notes
        for note_id, note in self.scale_notes.items():
            if note_id not in visible_notes:
                note.hide()

    def show_common_chord_tones(self, chord, scale_name=None, scale_key=None, scale_degree=None):
        if not self.common_chord_tones_visible:
            return

        m = parse_chord(chord)
        if not m:
            return

        harmonic_setting = (chord, scale_name, scale_key, scale_degree)
        if self.current_harmonic_settings == harmonic_setting:
            return

        chord_tone = m[1]
        if m[2]:
            chord_tone += m[2]
        chord_type = m[3]

        mappings = self.pattern_mapper.get_fret_mapping(chord_tone, chord_type, scale_name, scale_key, scale_degree)
        # mappings = self.tuning.get_fret_mapping(chord_tone, chord_spec, scale, scale_key, scale_degree)
        # self.current_harmonic_mapping = mappings
        # self.current_chord_type = chord_type
        # print("we got strong mappingz of mapping {}".format(mappings))

        for string_num, frets in mappings.items():
            if string_num >= self.tuning.num_strings or string_num < 0:
                continue
            for mapping in frets:
                if mapping and mapping[2]:
                    note_id = _generate_scale_note_id(string_num, mapping[0])
                    note = self.scale_notes.get(note_id)
                    if note and note.is_visible() and note.is_chord_tone():
                        note.set_common_tone(True)



    def is_in_mapping(self, string_num, fret_num):
        if not self.current_harmonic_mapping:
            return False
        mapping = self.current_harmonic_mapping.get(string_num)
        if not mapping:
            return None

        for m in mapping:
            if fret_num == m[0]:
                return True
            if fret_num > self.tuning.num_frets:
                return False

        return False


    def show_scales(self, show):
        self.scales_visible = show

    def update_scale_visibility(self, *args):
        for note_id, note in self.scale_notes.items():
            if not self.is_in_mapping(note.string_num, note.fret_num):
                continue
            if note.is_scale_tone() and not note.is_chord_tone():
                if self.scales_visible:
                    note.show()
                else:
                    note.hide()

    def show_arpeggio_tones(self, show):
        self.chord_tones_visible = show

    def set_common_chord_tones_visible(self, show):
        self.common_chord_tones_visible = show

    def update_chord_tones_visibility(self, *args):
        for note_id, note in self.scale_notes.items():
            if not self.is_in_mapping(note.string_num, note.fret_num):
                continue
            if note.is_chord_tone() and not note.is_scale_tone():
                if self.chord_tones_visible:
                    note.show()
                else:
                    note.hide()

    def add_tone_marker(self, string_num, fret_num, chord_label, chord_degree, scale_degree, is_playing=None):
        note_id = _generate_scale_note_id(string_num, fret_num)

        note = self.scale_notes.get(note_id)
        if note:
            if is_playing is not None:
                note.set_being_played(is_playing)
            else:
                note.set_scale_context(chord_label, chord_degree, scale_degree, is_playing)
                note.show()
        else:
            loc = self.get_finger_location(string_num, fret_num)

            pos_hint = {'center_x': loc[0]/self.width, 'center_y': loc[1]/self.height}
            size_hint = (self.finger_width_ratio, (self.finger_width_ratio * self.width / self.height))
            # print('pos_hint is {}'.format(pos_hint))

            note = ScaleNote(self, string_num, fret_num, chord_label, chord_degree, scale_degree, True if is_playing else False, pos_hint=pos_hint, size_hint=size_hint)
            self.scale_notes[note_id] = note
            self.add_widget(note)
        return note_id

    def highlight_tone_marker(self, string_num, fret_num, hide=False):
        note_id = _generate_scale_note_id(string_num, fret_num)

        note = self.scale_notes.get(note_id)
        if note:
            note.set_highlighted(not hide)

        return note_id


class Note(Widget):
    end_color = [0.1, 0.1, 1.0, 0.0]
    start_color = [0.8, 0.0, 0.0, 0.8]
    # fade_duration = 0.5
    fade_duration = 0.0

    def __init__(self, fretboard, string_num, fret_num, note_fade_time, **kwargs):
        super(Note, self).__init__(**kwargs)
        self.fretboard = fretboard
        self.string_num = string_num
        self.fret_num = fret_num
        self.fade_duration = note_fade_time
        self.id = _generate_note_id(string_num, fret_num)
        with self.canvas:
            self.color = Color(*self.start_color)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)

        self.bind(pos=self.do_update)
        self.bind(size=self.do_update)

    def do_update(self, *args):
        self.fretboard.update_note(self)
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size

    def hide(self):
        if self.fade_duration <= 0:
            self.color.rgba = self.end_color
            return
        # Animation.cancel_all(self.color, 'r,g,b,a')
        Animation.cancel_all(self.color)
        self.anim = Animation(r=self.end_color[0],
                         g=self.end_color[1],
                         b=self.end_color[2],
                         a=self.end_color[3],
                         duration=self.fade_duration)
        self.anim.start(self.color)

    def show(self):
        # print('note {} is cancelling and showing'.format(self.id))
        Animation.cancel_all(self.color)
        self.color.rgba = self.start_color

class StringActivity(Widget):

    finger_color = (0.1, 0.1, 1.0, 0.8)
    hidden = BooleanProperty(False)

    def __init__(self, string_num, **kwargs):
        super(StringActivity, self).__init__(**kwargs)
        self.string_num = string_num
        self.id = _generate_string_id(string_num)
        with self.canvas:
            self.color = Color(*self.finger_color)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
        self.do_draw()
        # self.bind(size=self.do_draw)
        self.bind(pos=self.do_draw)

    def do_draw(self, *args):
        with self.canvas:
            # self.canvas.clear()
            if not self.hidden:
                self.color.rgba = self.finger_color
                self.ellipse.pos = self.pos
                self.ellipse.size = self.size

    def on_hidden(self, instance, value):
        self.color.a = 0.0
        # self.do_draw()

class Tracer(Widget):

    end_color = [0.1, 0.1, 1.0, 0.0]
    start_color = [0.8, 0.0, 0.0, 0.5]
    inner_line_color = [0.0, 0.0, 0.0, 1]
    # fade_duration = 0.5
    fade_duration = 2.0

    def __init__(self, fretboard, string_start, fret_start, string_end, fret_end, fade_duration, line_thickness, **kwargs):
        super(Tracer, self).__init__(**kwargs)
        self.fretboard = fretboard
        self.string_start = string_start
        self.fret_start = fret_start
        self.string_end = string_end
        self.fret_end = fret_end
        self.fade_duration = max(0.01, fade_duration)
        self.outer_line_thickness = max(1,line_thickness)

        self.id = _generate_tracer_id(string_start, fret_start, string_end, fret_end)
        with self.canvas:
            self.outer_color = Color(*self.start_color)
            points = fretboard.get_tracer_points(self)
            # print("drawing goddam line {}".format(points))
            self.outer_line = Line(points=points, width=self.outer_line_thickness, cap='round')
            self.animate()

        self.bind(pos=self.do_update)

    def do_update(self, *args):
        points = self.fretboard.get_tracer_points(self)
        print("drawing line {}".format(points))
        self.outer_line.points = points

    def animate(self):
        if self.fade_duration <= 0:
            self.outer_color.rgba = self.end_color
            self.hide()
            return
        # Animation.cancel_all(self.color, 'r,g,b,a')
        Animation.cancel_all(self.outer_color)
        self.anim = Animation(r=self.end_color[0],
                         g=self.end_color[1],
                         b=self.end_color[2],
                         a=self.end_color[3],
                         duration=self.fade_duration)

        self.anim.bind(on_complete=self.hide)
        self.anim.start(self.outer_color)

    def hide(self, *args):
        self.fretboard.remove_widget(self)

    def show(self):
        # print('note {} is cancelling and showing'.format(self.id))
        Animation.cancel_all(self.outer_color)
        self.color.rgba = self.start_color


class ScaleNote(Widget):

    input_activity_color = [0.8, 0.0, 0.0, 0.8]
    scale_color = [0.0, 0.1, 0.6, 0.3]
    root_color = [0.0, 0.0, 0.0, 0.8]
    ninth_color = [0.0, 0.5, 0.0, 0.8]
    third_color = [0.0, 0.0, 0.7, 0.5]
    eleventh_color = [0.6, 0.0, 0.7, 0.5]
    fifth_color = [0.0, 0.5, 0.5, 0.8]
    thirteenth_color = [0.7, 0.5, 0.0, 0.5]
    seventh_color = [0.8, 0.7, 0.0, 0.6]
    highlight_color = [1.0, 0.0, 0.0, 0.0]
    common_tone_color = [0.19215686274509805, 0.9764705882352941, 0.12156862745098039, 0.0]

    highlight_color_inst = None

    degree_colors = {0: input_activity_color,
                     1: root_color,
                     2: ninth_color,
                     3: third_color,
                     4: eleventh_color,
                     5: fifth_color,
                     6: thirteenth_color,
                     7: seventh_color,
                     8: scale_color,
                     9: [0,0,0,0],
                     }

    highlighted = BooleanProperty(False)
    common_tone = BooleanProperty(False)
    common_tone_trigger = None
    being_played = False # indicating input activity

    def __init__(self, fretboard, string_num, fret_num, chord_label=None, chord_degree=8, scale_degree=None, being_played=False, **kwargs):
        super(ScaleNote, self).__init__(**kwargs)
        self.chord_label=chord_label
        self.being_played = being_played

        # if chord_degree is None:
        #     chord_degree = 8

        self.chord_degree = chord_degree
        self.scale_degree = scale_degree
        self.fretboard = fretboard
        self.string_num = string_num
        self.fret_num = fret_num
        self.id = _generate_scale_note_id(string_num, fret_num)
        with self.canvas:
            self.color = Color(*self._get_current_color())
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
            self.highlight_color_inst = Color(*self.highlight_color)
            self.centered_circle = Line(circle=(self.center_x, self.center_y, 50), width=6)
            self.common_tone_color_inst = Color(*self.common_tone_color)
            # self.centered_square = Rectangle(size=(self.width, self.height), pos=(-100, -100))
            self.centered_square = Line(rectangle=(self.x, self.y, self.width, self.height), width=4)


        self.label = Label()
        self.label.halign = 'center'
        self.label.max_lines = 1
        self.label.valign = 'center'
        self.label.size = self.size
        if chord_label:
            self.label.text = chord_label

        self.highlighted = False
        self.bind(highlighted=self.update_highlight)
        self.bind(common_tone=self.update_common_tone)

        self.add_widget(self.label)
        self.bind(pos=self.do_update)
        self.bind(size=self.do_update)

        self.common_tone_trigger = Clock.create_trigger(lambda x: self.hide_common_tone(), 0.5 )

    def is_chord_tone(self):
        return bool(self.chord_label)

    def is_scale_tone(self):
        return self.scale_degree is not None

    def is_being_played(self):
        return self.being_played

    def set_being_played(self, is_playing):
        if self.being_played == is_playing:
            return
        was_played = self.being_played
        self.being_played = is_playing
        if not is_playing:
            if self._should_show():
                self._update_color()
            else:
                self.hide()
        else:
            if self._should_show():
                self._update_color()
            else:
                self.show()

    def _should_show(self):
        return (self.chord_degree is not None and self.chord_degree > 0) or (self.scale_degree is not None and self.scale_degree >= 0)

    def _get_current_color(self):

        color_idx = 9
        if self.being_played:
            color_idx = 0
        elif self.chord_degree is not None and self.chord_degree > 0:
            color_idx = self.chord_degree
        elif self.scale_degree and self.scale_degree >= 0:
            color_idx = 8

        return self.degree_colors[color_idx]

    def _update_color(self):
        self.color.rgba = self._get_current_color()

    def set_scale_context(self, chord_label=None, chord_degree=8, scale_degree=None, being_played=None):

        self.chord_label = chord_label

        if being_played is not None:
            self.being_played = being_played


        self.chord_degree = chord_degree
        self.scale_degree = scale_degree
        # self.color.rgba = self.degree_colors[0 if self.being_played else self.chord_degree]
        self.common_tone_trigger()

        if chord_label:
            self.label.text = chord_label
        else:
            self.label.text = ''
            self.highlighted = False

        # self.is_showing = True

    def hide_common_tone(self):
        self.common_tone = False

    def do_update(self, *args):
        self.fretboard.update_note(self)
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size
        self.label.pos = self.pos
        self.label.size = self.size
        self._update_color()
        self.update_highlight()
        self.update_common_tone()

    def hide(self):

        # only actually hide if note isn't being played
        if not self.being_played:
            self.color.a = 0.0
            self.ellipse.size = (0,0)

        self.highlighted = False
        self.common_tone = False
        self.scale_degree = None
        self.chord_degree = None
        self.label.text = ''



    def is_visible(self):
        return self.color.a > 0.0

    def update_common_tone(self, *args):

        if self.common_tone:
            self.centered_square.rectangle = (self.x + 5, self.y + 5, self.width - 10, self.height - 10)
            # self.centered_square.pos = (-((self.center_x + 7.5)*0.5), -((self.center_y + 7.5)*0.5))
            # self.centered_square.size = self.size
            self.common_tone_color_inst.a = 1.0
        else:
            self.common_tone_color_inst.a = 0.0
            self.centered_square.rectangle = (0, 0, 0, 0)
        # self.set_highlighted(True)
        # self.color.a = 1.0

    def show(self):
        self._update_color()
        self.label.text = self.chord_label if self.chord_label is not None else ''
        self.ellipse.size = self.size
        self.update_highlight()
        self.update_common_tone()


    def update_highlight(self, *args):
        with self.canvas:
            if self.highlighted:
                self.highlight_color_inst.a = 0.8
                self.centered_circle.circle = (self.center_x, self.center_y, (self.width + 15) / 2)
            else:
                self.highlight_color_inst.a = 0.0
                self.centered_circle.circle = (0, 0, 0)

    def set_highlighted(self, highlight):
        self.highlighted = highlight

    def set_common_tone(self, common_tone):
        self.common_tone = common_tone


def _generate_note_id(string_num, fret_num):
    return 'Note-{}.{}'.format(string_num, fret_num)

def _generate_scale_note_id(string_num, fret_num):
    return 'ScaleNote-{}.{}'.format(string_num, fret_num)

def _generate_tracer_id(string_start, fret_start, string_end, fret_end):
    return 'Tracer-{}.{}.{}.{}'.format(string_start, fret_start, string_end, fret_end)

def _generate_string_id(string_num):
    return 'String-{}'.format(string_num)

def _dist_from_nut(scale, fret_num):
    return scale - (scale / (2 ** (float(fret_num) / 12.0)))

