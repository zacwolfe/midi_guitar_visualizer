from multiprocessing import get_context
import mido
from time import sleep
import ctypes
import re
import queue
from .utils import empty_queue
import functools
from kivy.core.window import Window

PLAYER_STATE_STOPPED = 0
PLAYER_STATE_PLAYING = 1
PLAYER_STATE_PAUSED = 2
PLAYER_STATE_KILLED = 3

METADATA_REGEX = r'([A-G]{1}[a-zA-Z0-9\#\/]*|\/)(?:\s)?(([A-G][b\#]{0,1})_([a-zA-Z0-9_]+)(\((\d)\))?)?(\|([0-9]+)\|)?'
METADATA_PATTERN = re.compile(METADATA_REGEX)

class MidiPlayer(object):
    ctx = get_context('spawn')
    shared_player_state = ctx.Value('i', PLAYER_STATE_STOPPED)
    output_port_queue = ctx.Queue()
    input_queue = ctx.Queue()
    midi_metadata_queue = ctx.Queue()

    def __init__(self):

        self.shared_output_port_name = self.ctx.Value(ctypes.c_wchar_p, "")
        self.player_process = self.ctx.Process(name="player", target=self.do_loop,
                                      args=(self.input_queue, self.midi_metadata_queue, self.shared_player_state, self.output_port_queue))
        self.player_process.start()
        sleep(2)


    def do_loop(self, input_queue, midi_metadata_queue, player_state, output_port_queue):
        Window.hide()
        try:
            output_port = None

            # if output_port_name:
            #     print("opening {}".format(output_port_name))
            # output_port = mido.open_output('IAC Driver Bus 1', autoreset=True)
            last_port_name = None
            output_port_name = None
            while player_state.value != PLAYER_STATE_KILLED:
                # new_state = input_queue.get_nowait()
                # if new_state:
                #     player_state = new_state
                # print("midi_player state is {} and port {}".format(player_state.value, "what"))
                if player_state.value == PLAYER_STATE_PLAYING:
                    try:
                        output_port_name = output_port_queue.get_nowait()
                    except queue.Empty:
                        pass

                    print("playing bich")
                    try:
                        print("output_port is {}".format(output_port_name))
                        if not output_port or (output_port_name and output_port_name != last_port_name):
                            print("opening {}".format(output_port_name))
                            if output_port:
                                output_port.close()
                            output_port = mido.open_output(name=output_port_name, autoreset=True)
                            last_port_name = output_port_name

                        if output_port:
                            while True:
                                if player_state.value == PLAYER_STATE_PAUSED:
                                    sleep(0.1)
                                    continue
                                elif player_state.value == PLAYER_STATE_STOPPED:
                                    empty_queue(input_queue)
                                    output_port.reset()
                                    break

                                elif player_state.value == PLAYER_STATE_KILLED:
                                    return

                                try:
                                    msg = input_queue.get(True, 1)
                                    if msg.type=='stop':
                                        midi_metadata_queue.put_nowait('##done##')

                                    # print("got mussuj {}".format(msg))
                                    sleep(msg.time)

                                    play_message(msg, midi_metadata_queue, output_port)
                                except queue.Empty:
                                    pass

                    except Exception as e:
                        print("Couldn't open port {}: {}".format(output_port_name, str(e)))

                sleep(0.1)

        except Exception as ex:
            print("MidiPlayer exception {}".format(ex))

    def set_player_state(self, new_state):
        self.shared_player_state.value = new_state

    def set_output_port_name(self, name):
        self.output_port_queue.put_nowait(name)

    def stop(self):
        self.shared_player_state.value = PLAYER_STATE_KILLED

        if self.player_process:
            self.player_process.join()

def play_message(msg, output_queue, output_port):
    if msg.type == 'lyrics' or msg.type == 'marker':
        # print("got lyric: {}".format(msg))
        if msg.text:
            result = parse_metadata(msg.text.strip(), msg.type == 'marker')
            # print("parsed lyric {}".format(result))
            if result:
                output_queue.put_nowait(result)
                # self.player_progress_callback(**result)
    else:
        output_port.send(msg)


@functools.lru_cache(maxsize=128)
def parse_metadata(txt, pre_chord=False):
    m = METADATA_PATTERN.match(txt.strip())
    if not m:
        return None
    else:
        return {'chord':m.group(1),'scale_type':m.group(4), 'scale_key': m.group(3), 'scale_degree': m.group(6), 'line_num': m.group(8), 'pre_chord': pre_chord}


