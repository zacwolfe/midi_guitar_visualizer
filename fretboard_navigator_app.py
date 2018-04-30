import kivy
kivy.require('1.10.0') # replace with your current kivy version !

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.widget import Widget

from kivy.graphics import Color, Ellipse, Line, Rectangle
from fretboard.fretboard import Fretboard

# root = Builder.load_string('''
# FloatLayout:
#     canvas.before:
#         Color:
#             rgba: 0, 1, 0, 1
#         Rectangle:
#             # self here refers to the widget i.e FloatLayout
#             pos: self.pos
#             size: self.size
#     Button:
#         text: 'Hello World!!'
#         size_hint: .5, .5
#         pos_hint: {'center_x':.5, 'center_y': .5}
# ''')

# class MyPaintWidget(Widget):
#
#     def on_touch_down(self, touch):
#         with self.canvas:
#             Color(1, 1, 0)
#             d = 30.
#             Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))

class FretboardNavigator(App):

    def build(self):
        # return Label(text='Hello World')
        fretb = Fretboard()
        def my_callback():
            fretb.add_some_stuff()
            Clock.schedule_once(lambda dt:my_callback2(), 3 )

        def my_callback2():
            fretb.remove_some_stuff()

        Clock.schedule_once(lambda dt: my_callback(), 3)
        # Clock.schedule_once(lambda dt:my_callback2, 6)
        return fretb
        # return MyPaintWidget()

if __name__ == '__main__':
    FretboardNavigator().run()