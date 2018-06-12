import mido
import collections
from kivy.app import App
from constants import current_time_millis
from time import time, sleep
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty
import re
import queue
from .midi_player import PLAYER_STATE_PLAYING, PLAYER_STATE_STOPPED, PLAYER_STATE_PAUSED
from util.alert_dialog import Alert
from .utils import empty_queue


def get_midi_ports():
    return mido.get_input_names()

def get_midi_output_ports():
    return mido.get_output_names()

def get_midi_defaults():
    return {
        'midi_port': '',
        'midi_output_port': '',
    }

METADATA_REGEX = r'([A-G]{1}[a-zA-Z0-9\#\/]*|\/)(?:\s)?(([A-G][b\#]{0,1})_([a-zA-Z0-9]+)(\((\d)\))?)?(\|([0-9]+)\|)?'
METADATA_PATTERN = re.compile(METADATA_REGEX)

class Midi(EventDispatcher):
    player_state = NumericProperty(PLAYER_STATE_STOPPED)

    def __init__(self, midi_player, note_filter, default_port, midi_callback, default_output_port, midi_output_callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.midi_player = midi_player
        self.note_filter = note_filter
        self.default_port = default_port
        self.midi_callback = midi_callback
        self.midi_output_callback = midi_output_callback
        self.output_port = None
        self.input_port = None
        self.midi_file_path = None
        self.midi_file = None
        self.player_state = PLAYER_STATE_STOPPED
        self.bind(player_state=self.player_state_changed)
        self.player_callback = None
        self.player_progress_callback = None
        self.set_default_output_port(default_output_port)

    def dismiss(self):
        App.get_running_app().open_settings()

    def open_input(self):
        try:
            self.input_port = mido.open_input(name=self.default_port, callback=self.midi_message_received)
            print("input midi port connected! {}".format(self.default_port))
        except IOError:
            Alert(title="Oops",
                  text='Could not load midi port {}. \nPlease select a valid midi input port'.format(self.default_port),
                  on_dismiss_callback=lambda *args: self.dismiss())

    def open_output(self):
        if self.default_output_port not in get_midi_output_ports():

            Alert(title="Oops",
                  text='Could not load midi port {}. \nPlease select a valid midi output port'.format(self.default_output_port),
                  on_dismiss_callback=lambda *args: self.dismiss())

    def midi_message_received(self, message):
        if message.type not in ['note_on', 'note_off']:
            return

        if not self.note_filter.filter_note(message):
            # print('skipping {}'.format(message))
            return

        self.midi_callback(message.note, message.channel, message.type == 'note_on', message.time)

    def shutdown(self):
        if self.input_port:
            self.input_port.close()

    def set_default_port(self, port, open_port=False):
        self.shutdown()
        self.default_port = port
        if open_port:
            self.open_input()

    def set_default_output_port(self, port, open_port=False):
        self.shutdown()
        self.default_output_port = port
        self.midi_player.set_output_port_name(port)
        if open_port:
            self.open_output()

    def set_midi_file(self, path):
        self.midi_file_path = path
        self.midi_file = mido.MidiFile(path)
        self.midi_messages = list(self.midi_file)

    def set_midi_output_callback(self, callback):
        self.midi_output_callback = callback

    def set_player_callback(self, callback):
        self.player_callback = callback

    def set_player_progress_callback(self, callback):
        self.player_progress_callback = callback

    def player_state_changed(self, *args):
        if self.player_callback:
            self.player_callback(self.player_state)

        self.midi_player.set_player_state(self.player_state)

        if self.player_state == PLAYER_STATE_STOPPED:
            self.meta_poll_trigger = None
            empty_queue(self.midi_player.midi_metadata_queue)



    def stop(self):
        print("we stoppin!!!!")
        self.player_state = PLAYER_STATE_STOPPED


    def play(self):
        if self.player_state == PLAYER_STATE_PLAYING:
            self.player_state = PLAYER_STATE_PAUSED
            return
        elif self.player_state == PLAYER_STATE_PAUSED:
            self.player_state = PLAYER_STATE_PLAYING
            return
        else:
            if self.midi_file and self.midi_messages:
                print("loading up midi_messages of len {} and input_queue empty: {}".format(len(self.midi_messages), self.midi_player.input_queue.empty()))
                for msg in self.midi_messages:
                    self.midi_player.input_queue.put(msg, block=True, timeout=2)
                self.midi_player.input_queue.put(mido.Message('stop'), block=True, timeout=2)

                self.meta_poll_trigger = Clock.create_trigger(self.poll_midi_metadata, 1/60)
                self.meta_poll_trigger()

            self.player_state = PLAYER_STATE_PLAYING

    def poll_midi_metadata(self, *args):
        if self.player_state == PLAYER_STATE_STOPPED:
            return

        while True:
            try:
                msg = self.midi_player.midi_metadata_queue.get_nowait()
                if msg == '##done##':
                    print("WE DUNN "+ msg)
                    self.stop()
                    return
                elif type(msg) is dict:
                    self.player_progress_callback(**msg)
                else:
                    print("type is {} and {}".format(type(msg), msg))
                    # self.output_port.send(msg)
            except queue.Empty:
                break

        if self.meta_poll_trigger:
            self.meta_poll_trigger()


class NoteFilter(object):
    note_queue = collections.deque(maxlen=3)
    min_velocity = 20
    open_string_min_velocity = 50
    max_fret_distance = 6
    max_seq_gap_millis = 250
    skip_open_strings = True

    def __init__(self, tuning):
        self.tuning = tuning

    def filter_note(self, message):
        # print("got message {}".format(message))

        now = current_time_millis()
        message.time = now
        if message.type == 'note_on':
            if (self.tuning.is_impossible_note(message.channel, message.note)):
                return
            if (self.tuning.is_open_string(message.channel, message.note) and (self.skip_open_strings or message.velocity < self.open_string_min_velocity)):
                return
            elif message.velocity < self.min_velocity:
                return
            else:
                if len(self.note_queue) > 0:
                    last_msg = self.note_queue[-1]
                    # print("the time diff is {} and dist {}".format(
                    #     now - last_msg.time,
                    #     self.tuning.get_distance(last_msg.channel, last_msg.note, message.channel, message.note)
                    # ))
                    if now - last_msg.time < self.max_seq_gap_millis and \
                            self.tuning.get_distance(last_msg.channel, last_msg.note, message.channel, message.note) > self.max_fret_distance:
                        print("skipping this interval cuz its wide...",  self.tuning.get_distance(last_msg.channel, last_msg.note, message.channel, message.note), now - last_msg.time)
                        return

            # if self.tuning.is_open_string(message.channel, message.note):
            #     print("got open string {}".format(message))

            self.note_queue.append(message)

        return message

    def get_note_queue(self):
        return list(self.note_queue)


def play_message(msg, output_queue, output_port=None):
    if msg.type == 'lyrics':
        print("got lyric: {}".format(msg))
        if msg.text:
            result = parse_metadata(msg.text.strip())
            print("parsed lyric {}".format(result))
            if result:
                output_queue.put_nowait(result)
                # self.player_progress_callback(**result)
    else:
        if output_port:
            output_port.send(msg)
        else:
            output_queue.put_nowait(msg)

def parse_metadata(txt):
    m = METADATA_PATTERN.match(txt.strip())
    if not m:
        return None
    else:
        return {'chord':m.group(1),'scale_type':m.group(4), 'scale_key': m.group(3), 'scale_degree': m.group(6), 'line_num': m.group(8)}
