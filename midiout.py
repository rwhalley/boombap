import time
import rtmidi
import threading
import midiparse as mp
import CONFIG as c
import mido


class MIDIPlayer():

    def __init__(self):

        self.triggered = False
        self.midiout = None
        self.available_ports = None



    def play_note(self,midis,ports):
        if c.THREADING_ACTIVE:
            x = threading.Thread(target=self.play_worker, args=(midis,ports),daemon=True)
            x.start()
            x.join()
        else:
            self.play_worker(midis,ports)


    def all_notes_off(self):
        midis = []
        ports = []
        for i in range(0,128):
            midis.append([144,i,0])
            ports.append(c.SYNTH)

        self.play_note(midis,ports)



    def play_worker(self,midis,ports):


        #self.available_ports = self.midiout.get_ports()


        try:
            for key in c.PORTS:
                if c.SYNTH in key:
                    port_num = c.PORTS[key]
                    self.midiout.open_port(port_num)

        except (IndexError("MIDI port not open")):
            print("virtual port")
            self.midiout.open_virtual_port("My virtual output")

        with mido.open_output('reface CP') as outport:
            #print(midi)
            #print("PLAY NOTE")
            #print(threading.active_count())
            #print(f"MIDI + {[hex(midi[0]),midi[1],midi[2]]}")
            # note_on = [0x90, 60, 90] # channel 1, middle C, velocity 112
            # note_off=[0x90, 60,0]
            # print(midi)
            for i, midi in enumerate(midis):
                    if c.SYNTH in ports[i]:
                        outport.send(midi)
            #time.sleep(0.2)
            #self.midiout.send_message(note_on)


            # if(midi[2]>0) and not self.triggered:
            #     print("YEAH BUDDY")
            #     self.midiout.send_message(note_on)
            #     self.triggered = True
        #del self.midiout




## Debug
#m = MIDIPlayer()
#m.play_note([0x90, 60, 90])
