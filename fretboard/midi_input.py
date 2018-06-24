from multiprocessing import Value, get_context
import mido
from time import sleep
import ctypes
import re
import queue
from .utils import empty_queue
import functools

INPUT_STATE_INACTIVE = 0
INPUT_STATE_ACTIVE = 1


class MidiInput(object):
    ctx = get_context('spawn')
    input_port_name_queue = ctx.Queue()
    # input_queue = ctx.Queue()
    midi_input_queue = ctx.Queue()

    def __init__(self):

        self.shared_input_port_name = self.ctx.Value(ctypes.c_wchar_p, "")
        self.input_process = self.ctx.Process(name="midi_input", target=self.do_loop,
                                              args=(self.midi_input_queue, self.input_port_name_queue))
        self.input_process.start()
        sleep(2)


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
                    msg = input_port.receive()
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
