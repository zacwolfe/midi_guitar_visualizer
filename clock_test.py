from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock, CyClockBaseFree
from kivy.config import Config

import time

class IncrediblyCrudeClock(Label):
    trigger = None
    def update(self, *args):
        self.text = time.asctime()
        if self.trigger:
            self.trigger.timeout = 1
            self.trigger()


class TimeApp(App):
    def build(self):
        Config.set('kivy', 'KIVY_CLOCK', 'free_all')
        Config.write()
        crudeclock = IncrediblyCrudeClock()
        # Clock.schedule_interval(crudeclock.update, 1)
        # trigger = Clock.create_trigger(crudeclock.update)
        trigger = Clock.create_trigger_free(crudeclock.update)
        crudeclock.trigger = trigger
        trigger.timeout = 1
        trigger()
        return crudeclock

if __name__ == "__main__":
    TimeApp().run()