from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle

class PlayerPanel(BoxLayout):

    def __init__(self, fretboard, **kwargs):
        super(PlayerPanel, self).__init__(**kwargs)
        self.fretboard = fretboard
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        button_panel = BoxLayout(orientation='horizontal', size_hint_y=None, size_hint_x=1)
        button_panel.center_x = self.center_y
        play_button = Button(id='play',text='play', size=(200, 100), size_hint=(None, None), on_press=self.button_press)
        rewind_button = Button(id='rewind', text='rewind', size=(200, 100), size_hint=(None, None), on_press=self.button_press)
        stop_button = Button(id='stop', text='stop', size=(200, 100), size_hint=(None, None), on_press=self.button_press)

        button_panel.add_widget(Widget())
        button_panel.add_widget(rewind_button)
        button_panel.add_widget(play_button)
        button_panel.add_widget(stop_button)
        button_panel.add_widget(Widget())



        # with self.curr_line_text.canvas:
        #     Color(0, 1, 0, 0.25)
        #     Rectangle(pos=self.curr_line_text.pos, size=self.curr_line_text.size)

        self.curr_line_text = Label(color=(1,0,0, 0.9), halign='left', id='curr_line', text='a-hole abundance', size_hint=(1, 0.1), font_size='26sp', outline_color=(0, 1, 0))
        self.mma_textarea = TextInput(id='mma_textarea', size_hint=(1, 0.8))


        self.add_widget(button_panel)
        self.add_widget(self.curr_line_text)
        self.add_widget(self.mma_textarea)

    def button_press(self, button):
        txt = 'mine ass {} has thrived for many a year'.format(button.id)
        self.curr_line_text.text = txt
        self.curr_line_text.texture_update()
        print(txt)







