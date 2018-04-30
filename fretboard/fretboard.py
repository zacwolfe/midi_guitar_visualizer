from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.window import Window
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.config import Config

class Fretboard(RelativeLayout):


    neck_taper = .08
    # neck_taper = .5
    line_width = 5
    fret_width = 6
    margin_size = 10
    height_ratio = .18
    num_frets = 22

    initial_width = 1800
    initial_screen_loc_x = 50
    initial_screen_loc_y = 400

    string_box_width = 50
    string_box_line_width = 3
    string_activation_width = 30
    string_activation_height = 30
    string_activation_color = (0.0, 1.0, 0.0, 1.0)


    nut_width_ratio = .01
    nut_line_width = 3
    nut_color = (.902, .541, 0.0, 0.5)

    string_inset_ratio = .07
    string_width = 3
    string_slot_width = 3
    num_strings = 6
    string_tuning = ['E2', 'A2', 'D3', 'G3', 'C3', 'F4']
    fret_dot_locations = [3,5,7,9,12,15,17,19,21]
    fret_color = (0.3, 0.3, 0.3, 0.5)

    dot_width_ratio = 0.015
    dot_height_ratio = 0.015

    finger_offset_ratio = 0.2
    finger_width_ratio = 0.02
    finger_height_ratio = 0.02
    finger_color = (0.1, 0.1, 1.0, 0.8)


    # Config.set('graphics', 'width', str(initial_width))
    # Config.set('graphics', 'height', str(int(initial_width * height_ratio)))
    # Config.set('graphics', 'position', 'custom')
    # Config.set('graphics', 'left', 100)
    # Config.set('graphics', 'top', 10)

    def __init__(self, **kwargs):
        super(Fretboard, self).__init__(**kwargs)

        self.notes = {}

        with self.canvas:
            print("WITH SHITTING...")
            # Window.size = (self.initial_width, self.initial_width * self.height_ratio + self.margin_size * 2)
            # Window.left = self.initial_screen_loc_x
            # Window.top = self.initial_screen_loc_y
            Window.clearcolor = (1, 1, 1, 1)
            Color(1,1,1,1, group='fb')
            self.rect = Rectangle(pos=self.pos, size=self.size, group='fb')
            # self.button = Button(text='Hello world', size_hint=(.6, .6),
            #                 pos_hint={'x': .2, 'y': .2})
            # self.add_widget(self.button)

            # note = Note(5, 2, pos_hint={'x':.5, 'y':.5},
            #             size_hint=(self.finger_width_ratio, self.finger_height_ratio))

            # note = Note(5, 2, pos_hint={'x':.2, 'top':.4},
            #             size_hint=(self.finger_width_ratio, self.finger_height_ratio))
            # self.add_widget(note)
            # self.redraw_fretboard()
            #
            # Rectangle(pos=self.pos, size=self.size)
            pass

        with self.canvas.before:

        # you can use this to add instructions rendered before
            print("BEFORE...")
            # self.draw_fretboard()
            pass

        with self.canvas.after:
            print("AFTER...")
            self.redraw_fretboard()
            pass

        self.bind(size=self.redraw_fretboard)
        # self.bind(pos=self.redraw_fretboard)

    def on_touch_down(self, touch):
        with self.canvas:
            # Color(1, 1, 0)
            # d = 30.
            # Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            print("touch! {},{}".format(touch.x, touch.y))
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
        hite = self.fretboard_height()
        taper_amt = hite * self.neck_taper * 0.5
        neck_len = self.neck_length()
        nut_width = self.nut_width(neck_len=neck_len)
        relative_taper_amt = ((neck_len - nut_width) / neck_len) * taper_amt
        points = (self.margin_size + nut_width,
                  self.margin_size + relative_taper_amt,
                  self.margin_size + nut_width,
                  self.margin_size + hite - relative_taper_amt)
        Color(0, 0, 0, group='fb')
        Line(points=points, width=self.string_box_line_width, cap='round', group='fb')
        Color(*self.nut_color, group='fb')
        Rectangle(pos=(self.margin_size, self.margin_size + relative_taper_amt), size=(nut_width, hite - relative_taper_amt*2), group='fb')
        self.draw_nut_string_slots()

    def draw_nut_string_slots(self):

        nut_width = self.nut_width()
        start_x = self.margin_size
        end_x = start_x + nut_width
        Color(0, 0, 0, group='fb')
        for offset in self.get_string_locations(0):
            Line(points=(start_x, self.margin_size + offset, end_x, self.margin_size + offset), width=self.string_slot_width, cap='round', group='fb')

    def draw_strings(self):
        nut_width = self.nut_width()
        start_x = self.margin_size + nut_width
        end_x = self.width - (self.margin_size + self.string_box_width)
        start_offsets = self.get_string_locations(0)
        end_offsets = self.get_string_locations(self.fretboard_length())
        Color(0, 0, 0, group='fb')
        for string_num in range(0, self.num_strings):
            Line(points=(start_x, self.margin_size + start_offsets[string_num],
                         end_x, self.margin_size + end_offsets[string_num]), width=self.string_width, cap='round', group='fb')


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

        last_x = 0
        for fret_num in range(1, self.num_frets):
            fret_x = self.get_fret_x(fret_num)
            relative_taper_amt = ((neck_len - (nut_width + fret_x)) / neck_len) * taper_amt + self.fret_width # adjust for line cap
            start_y = self.margin_size+relative_taper_amt
            end_y = self.margin_size+hite-relative_taper_amt
            points = (fret_x, start_y, fret_x, end_y)
            Color(*self.fret_color, group='fb')
            Line(points=points, width=self.fret_width, group='fb')
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


    def get_finger_location(self, fret_num, string_num):
        if fret_num == 0:
            return 0

        fret_x = self.get_fret_x(fret_num)
        prev_fret_x = self.get_fret_x(fret_num - 1)

        # neck_len = self.neck_length()
        finger_width = self.width*self.finger_width_ratio
        pos_x = fret_x - (fret_x - prev_fret_x)*self.finger_offset_ratio
        pos_y = self.get_string_locations(pos_x)[string_num] + self.margin_size
        if pos_x + finger_width*0.5 > fret_x:
            pos_x = fret_x - finger_width*0.5

        # pos_x = fret_x
        return (pos_x, pos_y)


    def note_on(self, string_num, fret_num):
        note_id = _generate_note_id(string_num, fret_num)

        if note_id in self.notes:
            print('note {} is already hear!!!!'.format(note_id))
            return

        loc = self.get_finger_location(fret_num, string_num)
        print('Note on at {},{}'.format(int(loc[0]), int(loc[1])))

        # neck_len = self.neck_length()

        # note = Note(string_num, fret_num, pos=(loc[0], loc[1]), size=(self.finger_width_ratio*neck_len, self.finger_height_ratio*neck_len))

        # pos_hint = {'x': loc[0]/self.width, 'y': loc[1]/self.height}
        pos_hint = {'center_x': loc[0]/self.width, 'center_y': loc[1]/self.height}
        print('pos_hint is {}'.format(pos_hint))

        # note = Note(string_num, fret_num, pos=(loc[0], loc[1]), size_hint=(self.finger_width_ratio, self.finger_height_ratio))
        note = Note(string_num, fret_num, pos_hint=pos_hint, size_hint=(self.finger_width_ratio, (self.finger_width_ratio*self.width/self.height)))
        # note = Note(string_num, fret_num, pos_hint=pos_hint, size=(self.finger_width_ratio*neck_len, self.finger_height_ratio*neck_len))
        self.notes[note_id] = note
        self.add_widget(note)
        # note.x = loc[0]
        # note.y = loc[1]
        # note.width = self.finger_width
        # note.height = self.finger_height



        # Color(*self.finger_color)
        # Ellipse(pos=(loc[0], loc[1]), size=(self.finger_width, self.finger_height))

    def note_off(self, string_num, fret_num):
        note_id = _generate_note_id(string_num, fret_num)
        note = self.notes.pop(note_id, None)
        if note:
            self.remove_widget(note)

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


    def get_intersection(self, string_num, fret_num):
        fret_x = self.get_fret_x(fret_num)

        hite = self.fretboard_height()
        taper_amt = hite * self.neck_taper * 0.5
        neck_len = self.neck_length()
        nut_width = self.nut_width(neck_len=neck_len)

        relative_taper_amt = ((neck_len - (nut_width + fret_x)) / neck_len) * taper_amt
        string_inset = self.string_inset_ratio * hite
        fret_x = self.get_fret_x(fret_num)


    # def show_finger(self, x_pos, y_pos):

    def get_string_locations(self, dist_from_nut):
        hite = self.fretboard_height()

        inset_hight = hite * self.string_inset_ratio
        string_span = hite - inset_hight * 2
        string_spacing = string_span/(self.num_strings - 1)

        taper_amt = hite * self.neck_taper * 0.5
        neck_len = self.neck_length()
        nut_width = self.nut_width(neck_len=neck_len)

        relative_taper_amt = ((neck_len - (nut_width + dist_from_nut)) / neck_len) * taper_amt
        board_height_pct = (hite - relative_taper_amt*2)/hite
        return [relative_taper_amt + board_height_pct*(inset_hight + (x*string_spacing)) for x in range(0, self.num_strings)]


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
        Line(points=self.get_fretboard_outline(), width=self.line_width, cap='round', group='fb')
        self.draw_string_box()
        self.draw_nut()
        self.draw_frets()
        self.draw_strings()
        # self.draw_notes()


    def get_normalized_fret_dist_to_nut(self, fret_num):
        if fret_num == 0:
            return 0.0

        s = 1.0
        return _dist_from_nut(s, fret_num)/_dist_from_nut(s, self.num_frets)


    def add_some_stuff(self):
        # self.note_on(0, 1)
        # self.note_on(1, 11)
        # self.note_on(2, 12)
        self.note_on(5, 5)
        self.note_on(5, 1)
        self.note_on(4, 22)

        self.draw_string_activation(2)

    def remove_some_stuff(self):
        self.note_off(0,1)
        self.note_off(1, 11)
        self.note_off(2, 12)
        pass
        # self.draw_finger_location(1, 0)
        # self.draw_finger_location(11, 1)
        # self.draw_finger_location(12, 2)
        # self.draw_finger_location(5, 5)
        # self.draw_finger_location(22, 4)
        #
        # self.draw_string_activation(2)

class Note(Widget):

    finger_color = (0.1, 0.1, 1.0, 0.8)

    def __init__(self, string_num, fret_num, **kwargs):
        super(Note, self).__init__(**kwargs)
        self.string_num = string_num
        self.fret_num = fret_num
        self.id = _generate_note_id(string_num, fret_num)
        self.do_draw()
        # self.bind(size=self.do_draw)
        self.bind(pos=self.do_draw)

    def do_draw(self, *args):
        with self.canvas:
            self.canvas.clear()
            Color(*self.finger_color)
            print("this note {} trying to draw with pos_hint {} and size {} and abs pos {} and size {}".format(
                self.id, self.pos_hint, self.size_hint, self.pos, self.size
            ))
            # Ellipse(pos=self.pos, size=(self.size[0], self.size[0]))
            Ellipse(pos=self.pos, size=self.size)
            # Ellipse(pos_hint=self.pos_hint, size_hint=self.size_hint)
            # Ellipse(size_hint=(1,1))
            # Ellipse(pos=self.pos, size=self.size)
            # print('my id is {}'.format(self.id))


def _generate_note_id(string_num, fret_num):
    return 'Note-{}.{}'.format(string_num, fret_num)

def _dist_from_nut(scale, fret_num):
    return scale - (scale / (2 ** (float(fret_num) / 12.0)))