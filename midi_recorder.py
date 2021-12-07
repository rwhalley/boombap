from midiparse import MIDIParse as mp
import QUNEO
import CONFIG as c
from operator import itemgetter
import note

class MIDIRecorder:
    def __init__(self,metronome):
        self.RECORD = False
        self.my_loops = {} # all stored loops
        self.my_loop = []  # current recording loop
        self.play_loops = {} # all stored loops being played
        self.metronome = metronome
        self.active_loops = []
        self.current_loop_length = 0
        self.current_loop_index = 0

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
        self.current_loop_length = 0
        self.current_loop_index = 0

    def clear_all_loops(self):
        self.my_loop = []
        self.my_loops = {}
        self.current_loop_length = 0
        self.current_loop_index = 0

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


    def add_entry_old(self, midi, port, when_added):
        pos = self.metronome.get_position(timestamp=when_added)
        note = midi.note
        bank = self.metronome.controller.current_bank
        port = port
        when_added = when_added
        entry = [pos, midi, bank, port, when_added]
        self.my_loop.append(entry)
        print("ENTRY ADDED")
        print(self.my_loop)

    def add_entry(self,midi,port,when_added):
        self.my_loop.append(note.Note(self.metronome.get_position(timestamp=when_added),
                                      midi,
                                      self.metronome.controller.current_bank,
                                      port,
                                      when_added))

        self.current_loop_length = len(self.my_loop)
        self.my_loop.sort(key=lambda x: x.bar_position) #resort the list every time a new item added


