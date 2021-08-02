import time
import rtmidi

class MIDIPlayer():

    def __init__(self):

        self.triggered = False
        self.midiout = rtmidi.MidiOut()
        self.available_ports = self.midiout.get_ports()

        if self.available_ports:
            self.midiout.open_port(0)
        else:
            self.midiout.open_virtual_port("My virtual output")


    def play_note(self,midi):
        with self.midiout:
            #print(midi)
            print("PLAY NOTE")
            #print(f"MIDI + {[hex(midi[0]),midi[1],midi[2]]}")
            note_on = [0x90, 60, 90] # channel 1, middle C, velocity 112
            note_off=[0x90, 60,0]
            #self.midiout.send_message(midi[0])
            #time.sleep(0.2)
            #self.midiout.send_message(note_on)


            # if(midi[2]>0) and not self.triggered:
            #     print("YEAH BUDDY")
            #     self.midiout.send_message(note_on)
            #     self.triggered = True


    def cleanup(self):
        del self.midiout
