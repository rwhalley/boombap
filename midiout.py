import time
import rtmidi
#import mido
import midiparse as mp
import CONFIG as c

class MIDIPlayer():

    def __init__(self):

        self.triggered = False
        self.midiout = None
        self.available_ports = None
        self.midiout = rtmidi.MidiOut()
        #self.rtmidi = mido.Backend('mido.backends.rtmidi')






          # may need to clean this up






    def all_notes_off(self):
        midis = []
        ports = []
        for i in range(0,128):
            midis.append([144,i,0])
            ports.append('reface CP')

        if len(midis)>0:
            self.play_note(midis,ports)

    def play_note(self,midis,port,play):
        with self.midiout:
            self.midiout.open_port(1)
            for midi in midis:
                self.midiout.send_message(midi)

        # with self.rtmidi.open_output('reface CP') as outport:
        #     for midi in midis:
        #         if midi[2]==0:
        #             note = 'note_off'
        #
        #         else:
        #             note = 'note_on'
        #
        #         message = mido.Message(note, note=midi[1], velocity=midi[2])
        #
        #         outport.send(message)

    # def play_note(self,midi,port,play):
    #
    #     # self.available_ports = self.midiout.get_ports()
    #     # if c.SYNTH in self.available_ports:
    #     #     for i,device in enumerate(c.port_names):
    #     #         if c.SYNTH in device:
    #
    #         # for port in self.available_ports:
    #         #     if c.SYNTH in port:
    #     self.available_ports = self.midiout.get_ports()
    #     if c.SYNTH in self.available_ports:
    #         for i,device in enumerate(c.port_names):
    #             if c.SYNTH in device:
    #
    #
    #                 with self.midiout:
    #                     self.midiout.open_port(1)
    #
    #                     #print(midi)
    #                     #print("PLAY NOTE")
    #                     #print(threading.active_count())
    #                     #print(f"MIDI + {[hex(midi[0]),midi[1],midi[2]]}")
    #                     # note_on = [0x90, 60, 90] # channel 1, middle C, velocity 112
    #                     # note_off=[0x90, 60,0]
    #                     # print(midi)
    #
    #                     #if c.SYNTH in port:
    #                     #print(port)
    #
    #                     self.midiout.send_message(midi)
    #                     self.midiout.close_port()
    #                     #self.midiout.send_message(note_on)
    #
    #
    #                     # if(midi[2]>0) and not self.triggered:
    #                     #     print("YEAH BUDDY")
    #                     #     self.midiout.send_message(note_on)
    #                     #     self.triggered = True
    #                     del self.midiout




## Debug
#m = MIDIPlayer()
#m.play_note([0x90, 60, 90])
