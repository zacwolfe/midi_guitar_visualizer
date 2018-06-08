from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window


class Alert(Popup):

    def __init__(self, title, text):
        super(Alert, self).__init__()
        content = BoxLayout(orientation="vertical")
        # content = AnchorLayout(anchor_x='center', anchor_y='bottom')
        content.add_widget(
            Label(text=text, halign='left', valign='top')
        )
        ok_button = Button(text='Ok', size_hint=(None, None), size=(200, 75))
        content.add_widget(ok_button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(None, None),
            size=(Window.width / 3, Window.height / 3),
            auto_dismiss=True,
        )
        ok_button.bind(on_press=popup.dismiss)
        popup.open()