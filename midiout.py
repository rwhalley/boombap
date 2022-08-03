import time
import threading
import midiparse as mp
import CONFIG as c
import mido
from note_class import Note


class MIDIPlayer():

    def __init__(self,ports, dev=c.SYNTH, light=False):
        # self.triggered = False
        # self.midiout = None
        # self.available_ports = None
        self.outport = None
        self.synth_present = False

        devs = mido.get_output_names()
        print(f"Output Devices: {devs}")

        if light:
            self.synth_present = False
            dev = c.MIDI_CONTROLLER
            for d in devs:
                if dev in d:
                    print(f"Opening LED Output Device: {d}")
                    self.outport = mido.open_output(d)
                    break
        else:
            for port in ports:
                if c.SYNTH in port:
                    for d in devs:
                        if dev in d:
                            self.synth_present = True
                            print(f"Opening Synth Output Device: {d}")
                            self.outport = mido.open_output(d)
                            break




    # ### PLAY MIDI NOTE
    #
    # def play_note(self,note):
    #     if c.THREADING_ACTIVE:
    #         x = threading.Thread(target=self.play_worker, args=(note,),daemon=True)
    #         x.start()
    #         x.join()
    #     else:
    #         self.play_worker(note)

    def play_note(self,note, light=False):
        if c.SYNTH in note.port:
            self.outport.send(note.midi)
        if light:
            self.outport.send(note.midi)


            # with mido.open_output(c.SYNTH) as outport:
            #
            #     outport.send(note.midi)
            #
            # outport.close()
            #print("before")
            #midiout = mido.open_output(note.port)
            #self.outport.send(note.midi)
            #midiout.close()
            #print("after")
            #self.outport.send(note.midi)




    def play_note_old(self,midis,ports):
        if c.THREADING_ACTIVE:
            x = threading.Thread(target=self.play_worker, args=(midis,ports),daemon=True)
            x.start()
            x.join()
        else:
            self.play_worker(midis,ports)


    def all_notes_off(self):
        if self.synth_present:
            for i in range(0,128):
                self.play_note(Note(0,mido.Message('note_off', note=i),0,c.SYNTH,time.time(), -2,0))



    def play_worker_old(self,midis,ports):
        print("YES")
        if c.SYNTH in ports:
            for midi in midis:
                print(midi)
                print("NO")
                self.outport.send(midi)

#     def play_worker_rtmidi(self,midis,ports):
#
#
#         #self.available_ports = self.midiout.get_ports()
#
#
#         try:
#             for key in c.PORTS:
#                 if c.SYNTH and c.SYNTH in key:
#                     port_num = c.PORTS[key]
#                     self.midiout.open_port(port_num)
#
#         except (IndexError("MIDI port not open")):
#             print("virtual port")
#             self.midiout.open_virtual_port("My virtual output")
#
#         with mido.open_output('reface CP') as outport:
#             #print(midi)
#             #print("PLAY NOTE")
#             #print(threading.active_count())
#             #print(f"MIDI + {[hex(midi[0]),midi[1],midi[2]]}")
#             # note_on = [0x90, 60, 90] # channel 1, middle C, velocity 112
#             # note_off=[0x90, 60,0]
#             # print(midi)
#             for i, midi in enumerate(midis):
#                 if c.SYNTH and c.SYNTH in ports[i]:
#                     outport.send(midi)
#             #time.sleep(0.2)
#             #self.midiout.send_message(note_on)
#
#
#             # if(midi[2]>0) and not self.triggered:
#             #     print("YEAH BUDDY")
#             #     self.midiout.send_message(note_on)
#             #     self.triggered = True
#         #del self.midiout
#
#
#
#
# ## Debug
# #m = MIDIPlayer()
# #m.play_note([0x90, 60, 90])
