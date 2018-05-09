from kivy.uix.settings import SettingItem, ObjectProperty, SettingSpacer
import kivy.utils as utils
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.button import Button

from kivy.lang import Builder

Builder.load_string(
'''#:import get_color kivy.utils.get_color_from_hex
<SettingColorPicker>:
    Label:
        color: get_color(root.value) if root.value else (1,1,1,1.)
        text: root.value or ''
''')


class SettingColorPicker(SettingItem):
    '''Implementation of a string setting on top of a :class:`SettingItem`.
    It is visualized with a :class:`~kivy.uix.label.Label` widget that, when
    clicked, will open a :class:`~kivy.uix.popup.Popup` with a
    :class:`~kivy.uix.textinput.Textinput` so the user can enter a custom
    value.
    '''

    popup = ObjectProperty(None, allownone=True)
    '''(internal) Used to store the current popup when it's shown.
    :attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    textinput = ObjectProperty(None)
    '''(internal) Used to store the current textinput from the popup and
    to listen for changes.
    :attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    def on_panel(self, instance, value):
        # print instance, value, "on_panel"
        if value is None:
            return
        self.bind(on_release=self._create_popup)

    def _dismiss(self, *largs):
        if self.textinput:
            self.textinput.focus = False
        if self.popup:
            self.popup.dismiss()
        self.popup = None

    def _validate(self, instance):
        self._dismiss()
        #value = self.textinput.text.strip()
        value = utils.get_hex_from_color(self.colorpicker.color)
        self.value = value

    def _create_popup(self, instance):
        # create popup layout
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
            title=self.title, content=content, size_hint=(None, 0.9),
            width=popup_width)

        # create the textinput used for numeric input
        # self.textinput = textinput = TextInput(
        #     text=self.value, font_size='24sp', multiline=False,
        #     size_hint_y=None, height='42sp')
        # textinput.bind(on_text_validate=self._validate)
        # self.textinput = textinput

        # construct the content, widget are used as a spacer
        # content.add_widget(Widget())
        # content.add_widget(textinput)
        self.colorpicker = colorpicker = ColorPicker(color=utils.get_color_from_hex(self.value))
        colorpicker.bind(on_color=self._validate)

        self.colorpicker = colorpicker
        content.add_widget(colorpicker)
        # content.add_widget(Widget())
        content.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        btnlayout = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        btn = Button(text='Ok')
        btn.bind(on_release=self._validate)
        btnlayout.add_widget(btn)
        btn = Button(text='Cancel')
        btn.bind(on_release=self._dismiss)
        btnlayout.add_widget(btn)
        content.add_widget(btnlayout)

        # all done, open the popup !
        popup.open()

    def on_value(self, instance, value):
        print('i got a fucking value {}'.format(value))
        super(SettingColorPicker, self).on_value(instance, value)
