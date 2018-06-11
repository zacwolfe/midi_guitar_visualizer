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
        self.midi_playback_trigger = None
        self.player_callback = None
        self.player_progress_callback = None
        self.set_default_output_port(default_output_port)


    def open_input(self):
        if self.default_port not in get_midi_ports():
            def dismiss():
                App.get_running_app().open_settings()

            Alert(title="Oops",
                  text='Could not load midi port {}. \nPlease select a valid midi input port'.format(self.default_port),
                  on_dismiss_callback=lambda *args: dismiss())


    def open_output(self):
        if self.default_output_port not in get_midi_output_ports():
            def dismiss():
                App.get_running_app().open_settings()

            Alert(title="Oops",
                  text='Could not load midi port {}. \nPlease select a valid midi output port'.format(self.default_output_port),
                  on_dismiss_callback=lambda *args: dismiss())

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
        self.midi_file_pointer = 0

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



    def stop(self):
        print("we stoppin!!!!")
        self.player_state = PLAYER_STATE_STOPPED
        self.midi_file_pointer = 0
        self.midi_playback_trigger = None


    def play(self):
        if self.player_state == PLAYER_STATE_PLAYING:
            self.player_state = PLAYER_STATE_PAUSED
        elif self.player_state == PLAYER_STATE_PAUSED:
            self.player_state = PLAYER_STATE_PLAYING
        else:
            self.player_state = PLAYER_STATE_PLAYING

        if self.midi_file and self.midi_messages:
            for msg in self.midi_messages:
                self.midi_player.input_queue.put_nowait(msg)

            self.midi_player.set_player_state(PLAYER_STATE_PLAYING)
            # self.midi_play_last = time()
            # self._do_play_loop()

            # self.player_thread = Thread(name="player", target=self._do_play)
            # self.player_thread.start()
            # self.midi_metadata_queue = Queue()
            # self.player_process = Process(name="player", target=self._do_play, args=(self.midi_messages, self.midi_metadata_queue, self.shared_player_state,self.default_output_port))
            # self.player_process.start()
            self.meta_poll_trigger = Clock.create_trigger(self.poll_midi_metadata, 1/60)
            self.meta_poll_trigger()

    def poll_midi_metadata(self, *args):
        if self.player_state == PLAYER_STATE_STOPPED:
            return

        while True:
            try:
                msg = self.midi_player.midi_metadata_queue.get_nowait()
                if type(msg) is dict:
                    self.player_progress_callback(**msg)
                else:
                    print("type is {} and {}".format(type(msg), msg))
                    # self.output_port.send(msg)
            except queue.Empty:
                break

        if self.meta_poll_trigger:
            self.meta_poll_trigger()


    def _do_play(self, midi_messages, output_queue, player_state, output_port_name):
        output_port = None
        try:
            print("opening {}".format(output_port_name))

            # output_port = mido.open_output(name=output_port_name, autoreset=True)
            idx = 0
            while True:
                # new_state = input_queue.get_nowait()
                # if new_state:
                #     player_state = new_state

                if player_state == PLAYER_STATE_STOPPED:
                    break
                elif player_state == PLAYER_STATE_PAUSED:
                    sleep(0.1)
                    continue

                msg = midi_messages[idx]
                sleep(msg.time)

                play_message(msg, output_queue, output_port)

                idx += 1

            if output_port:
                output_port.close()

        except IndexError:
            return





    def _do_play_loop(self, *args):
        if self.player_state == PLAYER_STATE_PAUSED or self.player_state == PLAYER_STATE_PAUSED:
            return

        try:
            i = self.midi_file_pointer
            msg = self.midi_messages[i]

            if i > 0:
                since_last = time() - self.midi_play_last
                print("error was {}".format(since_last - msg.time))

            i += 1
            self.play_message(msg)

            while True:
                msg = self.midi_messages[i]
                if msg.time < 0.0001:
                    self.play_message(msg)
                    i +=1
                else:
                    break


            self.midi_file_pointer = i
            if not self.midi_playback_trigger:
                self.midi_playback_trigger = Clock.create_trigger_free(self._do_play_loop)

            self.midi_play_last = time()
            self.midi_playback_trigger.timeout = msg.time
            print("next trigga is {}".format(msg.time))
            self.midi_playback_trigger()

        except:
            print("fuggered")
            self.stop()






    def _do_play_old(self):
        for msg in self.midi_file.play(meta_messages=True):
            self.play_message(msg)
            if self.player_state != PLAYER_STATE_PLAYING:
                break  # TODO: handle pause/resume
        print("Dunn playin!!!!")




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