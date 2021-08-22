import time
import rtmidi
import threading
import midiparse as mp

class MIDIPlayer():

    def __init__(self):

        self.triggered = False
        self.midiout = None
        self.available_ports = None



    def play_note(self,midis):

        x = threading.Thread(target=self.play_worker, args=(midis,),daemon=True)
        x.start()
        x.join()


    def all_notes_off(self):
        midis = []
        for i in range(0,128):
            midis.append([144,i,0])

        self.play_note(midis)



    def play_worker(self,midis):
        self.midiout = rtmidi.MidiOut()
        #self.available_ports = self.midiout.get_ports()


        try:
            self.midiout.open_port(1)
        except (IndexError("MIDI port not open")):
            print("virtual port")
            self.midiout.open_virtual_port("My virtual output")

        with self.midiout:
            #print(midi)
            #print("PLAY NOTE")
            #print(threading.active_count())
            #print(f"MIDI + {[hex(midi[0]),midi[1],midi[2]]}")
            # note_on = [0x90, 60, 90] # channel 1, middle C, velocity 112
            # note_off=[0x90, 60,0]
            # print(midi)
            for i, midi in enumerate(midis):
                    self.midiout.send_message(midi)
            #time.sleep(0.2)
            #self.midiout.send_message(note_on)


            # if(midi[2]>0) and not self.triggered:
            #     print("YEAH BUDDY")
            #     self.midiout.send_message(note_on)
            #     self.triggered = True
        del self.midiout




## Debug
#m = MIDIPlayer()
#m.play_note([0x90, 60, 90])
