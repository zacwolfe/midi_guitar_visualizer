from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from .fretboard import Fretboard
class AppWindow(RelativeLayout):

    height_ratio = .36
    initial_width = 1800
    initial_screen_loc_x = 50
    initial_screen_loc_y = 400

    def __init__(self, **kwargs):
        super(AppWindow, self).__init__(**kwargs)

        with self.canvas:
            Window.size = (self.initial_width, self.initial_width * self.height_ratio)
            Window.left = self.initial_screen_loc_x
            Window.top = self.initial_screen_loc_y
            Window.clearcolor = (1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, group='fb')
            self.fretboard = Fretboard(pos_hint={'x':0, 'y':0}, size_hint=(1, 0.5))
            self.add_widget(self.fretboard)


        with self.canvas.before:
            pass

        with self.canvas.after:
            pass

        self.bind(size=self.size_changed)

    def size_changed(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

