from multiprocessing import Value, get_context
import mido
from time import sleep
import ctypes
import re
import queue
from .utils import empty_queue
import functools
from constants import current_time_millis

INPUT_STATE_INACTIVE = 0
INPUT_STATE_ACTIVE = 1


class MidiInput(object):
    ctx = get_context('spawn')
    input_port_name_queue = ctx.Queue()
    # input_queue = ctx.Queue()
    midi_input_queue = ctx.Queue(maxsize=1000)

    def __init__(self):

        self.shared_input_port_name = self.ctx.Value(ctypes.c_wchar_p, "")
        self.input_process = self.ctx.Process(name="midi_input", target=self.do_loop,
                                              args=(self.midi_input_queue, self.input_port_name_queue))
        self.input_process.start()

        # self.shred_process = self.ctx.Process(name="shred", target=self._do_shred,
        #                                       args=(self.midi_input_queue,))
        # self.shred_process.start()
        # sleep(2)



    def _do_shred(self, midi_input_queue):
        ascending=True
        current_note=0
        notes_up = [(45,5), (47,5), (48,5), (49, 5), (51,4), (52,4),(54,4), (56, 3), (57, 3), (59,3), (61, 2), (62, 2), (63, 2), (64, 2), (66, 1), (68, 1), (69, 1), (71, 0), (73, 0), (74, 0)]

        while True:
            if current_note >= len(notes_up):
                ascending = False
                current_note = len(notes_up) - 1
            elif current_note < 0:
                ascending = True
                current_note = 0

            note = notes_up[current_note]
            midi_input_queue.put_nowait(mido.Message('note_on', note=note[0], channel=note[1], velocity=100, time=0))
            sleep(0.02)
            midi_input_queue.put_nowait(mido.Message('note_off', note=note[0], channel=note[1], velocity=100, time=200))
            if ascending:
                current_note += 1
            else:
                current_note -= 1

    def do_loop(self, midi_input_queue, input_port_name_queue):
        try:
            input_port = None

            # if input_port_name:
            #     print("opening {}".format(input_port_name))
            # input_port = mido.open_output('IAC Driver Bus 1', autoreset=True)
            last_port_name = None
            input_port_name = None
            while True:
                # new_state = input_queue.get_nowait()
                # if new_state:
                #     player_state = new_state
                # print("midi_player state is {} and port {}".format(player_state.value, "what"))
                try:
                    # input_port_name = input_port_name_queue.get(block=True, timeout=3)
                    input_port_name = input_port_name_queue.get_nowait()
                except queue.Empty:
                    input_port_name = None
                    pass

                if input_port_name:
                    if input_port_name == '##done##':
                        return
                    try:

                        if not input_port or (input_port_name and input_port_name != last_port_name):
                            print("input_port is {}".format(input_port_name))
                            print("opening {}".format(input_port_name))
                            if input_port:
                                input_port.close()
                            # input_port = mido.open_input(name=input_port_name,callback=self.midi_message_received)
                            input_port = mido.open_input(name=input_port_name)
                            last_port_name = input_port_name

                    except Exception as e:
                        print("Couldn't open port {}: {}".format(input_port_name, str(e)))
                        midi_input_queue.put_nowait(e)
                        input_port = None

                if input_port:
                    # TODO: it sucks that there isn't a timeout allowed here!!
                    msg = input_port.receive(timeout=5)
                    if msg:
                        midi_input_queue.put_nowait(msg)



        except Exception as ex:
            print("MidiPlayer exception {}".format(ex))

    def set_input_port_name(self, name):
        self.input_port_name_queue.put_nowait(name)

    def stop(self):
        self.input_port_name_queue.put_nowait('##done##')

        if self.input_process:
            self.input_process.join()


    def midi_message_received(self, message):
        print("putting {}".format(message))
        self.midi_input_queue.put_nowait(message)
        # if message.type not in ['note_on', 'note_off']:
        #     return
        #
        # if not self.note_filter.filter_note(message):
        #     # print('skipping {}'.format(message))
        #     return
        #
        # self.midi_callback(message.note, message.channel, message.type == 'note_on', message.time)
