from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget


class InputDialog(Popup):

    def __init__(self, title, current_name, on_save, **kwargs):  # my_widget is now the object where popup was called from.
        super(InputDialog,self).__init__(**kwargs)
        self.on_save = on_save
        self.title = title
        self.name_input = TextInput(text='' if not current_name else current_name, size_hint=(None, None), size=(465, 35))
        self.content = BoxLayout(orientation="vertical", padding=(5,5,5,5))
        self.content.add_widget(self.name_input)

        button_panel = BoxLayout(orientation="horizontal")

        self.save_button = Button(text='Save', size_hint=(None, None), size=(100, 35))
        self.save_button.bind(on_press=self.save)

        self.cancel_button = Button(text='Cancel', size_hint=(None, None), size=(100, 35))
        self.cancel_button.bind(on_press=self.cancel)

        button_panel.add_widget(Widget())
        button_panel.add_widget(self.save_button)
        button_panel.add_widget(self.cancel_button)

        self.content.add_widget(button_panel)
        self.size_hint = (None, None)
        self.size = (500, 150)

    def save(self,*args):
        print("save %s" % self.name_input.text) # and you can access all of its attributes
        #do some save stuff
        self.on_save(self.name_input.text)
        self.dismiss()

    def cancel(self,*args):
        print("cancel")
        self.dismiss()


def open_saveas_dialog(current_name, on_save):
    save_popup = InputDialog('Save As...', current_name, on_save)
    save_popup.open()

