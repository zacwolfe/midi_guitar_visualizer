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
from .midi_input import MidiInput

from mido.midifiles.tracks import _to_abstime, _to_reltime, fix_end_of_track, MidiTrack
from mido.midifiles.units import tick2second, second2tick
from mido.midifiles.meta import MetaMessage

DEFAULT_TEMPO = 500000
def get_midi_ports():
    return mido.get_input_names()

def get_midi_output_ports():
    return mido.get_output_names()

def get_midi_defaults():
    return {
        'midi_port': '',
        'midi_output_port': '',
        'preload_chord_amt': 0.7,
        'common_chord_tone_amt': 1.5,
    }

METADATA_REGEX = r'([A-G]{1}[a-zA-Z0-9\#\/]*|\/)(?:\s)?(([A-G][b\#]{0,1})_([a-zA-Z0-9]+)(\((\d)\))?)?(\|([0-9]+)\|)?'
METADATA_PATTERN = re.compile(METADATA_REGEX)

class Midi(EventDispatcher):
    player_state = NumericProperty(PLAYER_STATE_STOPPED)

    def __init__(self, midi_player, note_filter, default_port, midi_callback, default_output_port, midi_output_callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.midi_player = midi_player
        self.midi_input =  MidiInput()
        self.note_filter = note_filter
        self.default_port = default_port
        self.midi_callback = midi_callback
        self.midi_output_callback = midi_output_callback
        self.midi_file_path = None
        self.midi_file = None
        self.player_state = PLAYER_STATE_STOPPED
        self.bind(player_state=self.player_state_changed)
        self.player_callback = None
        self.player_progress_callback = None
        self.set_default_output_port(default_output_port)
        self.set_default_input_port(default_port)
        self.preload_chord_amt = 1.0
        self.common_chord_tone_amt = 2.0
        self.start_midi_input()

    def dismiss(self):
        App.get_running_app().open_settings()

    def open_input(self):
        if self.default_port not in get_midi_ports():

            Alert(title="Oops",
                  text='Could not load input midi port {}. \nPlease select a valid midi inpput port'.format(self.default_port),
                  on_dismiss_callback=lambda *args: self.dismiss())


    def open_output(self):
        if self.default_output_port not in get_midi_output_ports():

            Alert(title="Oops",
                  text='Could not load midi port {}. \nPlease select a valid midi output port'.format(self.default_output_port),
                  on_dismiss_callback=lambda *args: self.dismiss())

    def midi_message_received(self, message):
        # print("m dikly {}".format(message))
        if message.type not in ['note_on', 'note_off']:
            return

        if not self.note_filter.filter_note(message):
            # print('skipping {}'.format(message))
            return

        self.midi_callback(message.note, message.channel, message.type == 'note_on', message.time)

    def set_default_input_port(self, port, open_port=False):

        self.default_port = port
        self.midi_input.set_input_port_name(port)
        if open_port:
            self.open_input()

    def set_default_output_port(self, port, open_port=False):
        self.default_output_port = port
        self.midi_player.set_output_port_name(port)
        if open_port:
            self.open_output()

    def set_midi_file(self, path, tempo):
        self.midi_file_path = path
        self.midi_file = mido.MidiFile(path)
        # self.midi_messages = list(self.midi_file)
        self.midi_messages = list(self.get_midi_messages(self.midi_file))

    def merge_tracks(self, tracks, ticks_per_beat):
        """Returns a MidiTrack object with all messages from all tracks.

        The messages are returned in playback order with delta times
        as if they were all in one track.
        """
        messages = []
        for track in tracks:
            messages.extend(_to_abstime(track))

        aux_msgs = list()
        print("Preload amt {} and common tone {}".format(self.preload_chord_amt, self.common_chord_tone_amt))
        for msg in messages:
            if (self.preload_chord_amt > 0.0 or self.preload_chord_amt > 0.0) and msg.type == 'lyrics' and msg.time >= ticks_per_beat * self.preload_chord_amt:  # push lyrics back a bit
                if self.common_chord_tone_amt > 0.0:
                    m = MetaMessage(type='marker', time = msg.time -  ticks_per_beat*self.common_chord_tone_amt, text=msg.text)
                    aux_msgs.append(m)

                if self.preload_chord_amt > 0.0:
                    msg.time -= ticks_per_beat * self.preload_chord_amt

        messages += aux_msgs
        messages.sort(key=lambda msg: msg.time)

        return MidiTrack(fix_end_of_track(_to_reltime(messages)))

    def get_midi_messages(self, midi_file):
        tempo = DEFAULT_TEMPO
        merged = self.merge_tracks(midi_file.tracks, midi_file.ticks_per_beat)

        for msg in merged:
            # Convert message time from absolute time
            # in ticks to relative time in seconds.
            if msg.time > 0:
                delta = tick2second(msg.time, midi_file.ticks_per_beat, tempo)
            else:
                delta = 0

            yield msg.copy(time=delta)

            if msg.type == 'set_tempo':
                tempo = msg.tempo

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

    def poll_midi_input(self, *args):
        while True:
            try:
                msg = self.midi_input.midi_input_queue.get_nowait()
                # print("got somethi {}".format(msg))
                if isinstance(msg, Exception):
                    Alert(title="Oops",
                          text='Could not load input midi port {}. \nPlease select a valid midi inpput port. Exception: {}'.format(
                              self.default_port, str(msg)),
                          on_dismiss_callback=lambda *args: self.dismiss())
                    break

                else:
                    self.midi_message_received(msg)
            except queue.Empty:
                break

        if self.input_poll_trigger:
            self.input_poll_trigger()

    def shutdown(self):
        self.midi_input.stop()

    def stop(self):
        print("we stoppin!!!!")
        self.player_state = PLAYER_STATE_STOPPED

    def start_midi_input(self):
        self.input_poll_trigger = Clock.create_trigger_free(self.poll_midi_input, 0)
        # self.input_poll_trigger = Clock.create_trigger(self.poll_midi_input, 0)
        self.input_poll_trigger()

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
                        # print("skipping this interval cuz its wide...",  self.tuning.get_distance(last_msg.channel, last_msg.note, message.channel, message.note), now - last_msg.time)
                        return

            # if self.tuning.is_open_string(message.channel, message.note):
            #     print("got open string {}".format(message))

            self.note_queue.append(message)

        return message

    def get_note_queue(self):
        return list(self.note_queue)

