from midiparse import MIDIParse as mp

class MIDIRecorder:
    def __init__(self,metronome):
        self.RECORD = False
        self.my_loops = []
        self.my_loop = []
        self.metronome = metronome

    def start_record (self):
        self.RECORD = True

    def play_loop(self,thresh,pos):
        notes = []
        for note in self.my_loop:
            if abs(note[0] - pos) < thresh:
                notes.append(note[1])
        return notes

    def stop_record(self):
        self.RECORD = False

    def save_loop(self):
        self.my_loops.append(self.my_loop)

    def clear_current_loop(self):
        self.my_loop = []

    def clear_all_loops(self):
        self.my_loops = []

    def set_current_loop(self,i):
        try:
            self.my_loop = self.my_loops[i]
        except IndexError("loop index not found"):
            pass

    def add_entry(self, midi):
        pos = self.metronome.get_position()
        note = mp.getNoteNumber(midi)
        bank = self.metronome.controller.current_bank
        entry = [pos, midi, bank]
        self.my_loop.append(entry)
        # if len(self.my_loop)>0 and self.my_loop[-1][1]>pos:
        #     self.my_loops.append(self.my_loop)
        #     self.my_loop = []
        # else:


