import time
import rtmidi

class MIDIPlayer():

    def __init__(self):


        self.midiout = rtmidi.MidiOut()
        self.available_ports = self.midiout.get_ports()

        if self.available_ports:
            self.midiout.open_port(0)
        else:
            self.midiout.open_virtual_port("My virtual output")


    def play_note(self,midi):
        with self.midiout:
            #note_on = [0x90, 60, 112] # channel 1, middle C, velocity 112
            self.midiout.send_message(midi)


    def cleanup(self):
        del self.midiout
