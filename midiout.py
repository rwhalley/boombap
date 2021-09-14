import time
import rtmidi
import midiparse as mp
import CONFIG as c

class MIDIPlayer():

    def __init__(self):

        self.triggered = False
        self.midiout = None
        self.available_ports = None
        self.midiout = rtmidi.MidiOut()  # may need to clean this up



    def play_note(self,midis,ports):

        # x = threading.Thread(target=self.play_worker, args=(midis,ports),daemon=True)
        # x.start()
        # x.join()
        self.play_worker(midis,ports)


    def all_notes_off(self):
        midis = []
        ports = []
        for i in range(0,128):
            midis.append([144,i,0])
            ports.append('reface CP')

        if len(midis)>0:
            self.play_note(midis,ports)



    def play_worker(self,midis,ports):


        self.available_ports = self.midiout.get_ports()
        if c.SYNTH in self.available_ports:

            for port in self.available_ports:
                if c.SYNTH in port:
                    self.midiout.open_port(name=port)


            with self.midiout:
                #print(midi)
                #print("PLAY NOTE")
                #print(threading.active_count())
                #print(f"MIDI + {[hex(midi[0]),midi[1],midi[2]]}")
                # note_on = [0x90, 60, 90] # channel 1, middle C, velocity 112
                # note_off=[0x90, 60,0]
                # print(midi)
                for i, midi in enumerate(midis):
                        if ports[i] == c.SYNTH:
                            self.midiout.send_message(midi)
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
