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

    def add_entry(self,pos, midi):
        #pos = self.metronome.get_position()
        note = mp.getNoteNumber(midi)
        entry = (pos, midi)
        self.my_loop.append(entry)
        # if len(self.my_loop)>0 and self.my_loop[-1][1]>pos:
        #     self.my_loops.append(self.my_loop)
        #     self.my_loop = []
        # else:


