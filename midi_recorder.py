from midiparse import MIDIParse as mp
import QUNEO
import CONFIG as c
from operator import itemgetter

class MIDIRecorder:
    def __init__(self,metronome):
        self.RECORD = False
        self.my_loops = {} # all stored loops
        self.my_loop = []  # current recording loop
        self.play_loops = {} # all stored loops being played
        self.metronome = metronome
        self.active_loops = []

    def start_record (self):
        self.RECORD = True

    def switch_record_button(self):
        if self.RECORD:
            print("LOOP RECORD OFF")
            self.stop_record()
        else:
            print("LOOP RECORD ON")
            self.start_record()



    def play_loop(self,thresh,pos): #
        notes = []

        # --- Add notes in the current recording loop ---
        for note in self.my_loop:
            if abs(note[0] - pos) < thresh:
                notes.append(note[1])

        # ---  Add notes from active stored loops ---
        for key in self.play_loops:
            for note in self.play_loops[key]:

                if abs(note[0] - pos) < thresh:
                    notes.append(note[1])

        print(f"NOTES {notes}")
        return notes


    def stop_record(self):
        self.RECORD = False

    def save_loop(self,id):
        self.my_loops[id]=(self.my_loop)

    def clear_current_loop(self):
        self.my_loop = []

    def clear_all_loops(self):
        self.my_loops = {}

    def add_play_loop(self,i):
        try:
            self.play_loops[i] = self.my_loops[i]
            self.active_loops.append(i)
        except IndexError("loop index not found"):
            pass


    def remove_play_loop(self,i):
        try:
            self.play_loops.pop(i,None)
            self.active_loops.remove(i)
        except IndexError("loop index not found"):
            pass


    def add_entry(self, midi, port, when_added):
        pos = self.metronome.get_position()
        note = mp.getNoteNumber(midi)
        bank = self.metronome.controller.current_bank
        port = port
        when_added = when_added
        entry = [pos, midi, bank, port, when_added]
        i = note - QUNEO.PAD_START
        #if port == "QUNEO" and (i<0 or i>15):
        #    raise IndexError
        #else:
        self.my_loop.append(entry)


        # if len(self.my_loop)>0 and self.my_loop[-1][1]>pos:
        #     self.my_loops.append(self.my_loop)
        #     self.my_loop = []
        # else:


