import time
from soundy_pygame import Soundy

class Metronome:
    def __init__(self, bpm=120, path=None):
        self.is_on = False
        self.bpm = bpm
        self.beat_length = int(60 / self.bpm * 1000)
        self.max_beats = 4
        self.notes_per_beat = 3
        self.max_notes = self.max_beats * self.notes_per_beat
        self.measure_length = int(self.beat_length * 4)
        self.note_length = int(self.beat_length / 4)
        self.last_time = 0
        self.current_note = 0
        self.current_beat = 0
        self.sound = Soundy(path)
        self.metronome_seq_kaolack = [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0]
        self.metronome_seq_lumbuel = [1,0,0,0,1,0,1,0,0,1,0,0]


    def _update_interval(self, new_bpm):
        self.beat_length = int(60 / new_bpm * 1000)
        self.measure_length = int(self.beat_length * 4)
        self.note_length = int(self.beat_length / 4)


    def switch(self):
        self.is_on = not self.is_on


    def set_bpm(self,input):
        self.wait = True
        new_bpm = 40+input*200
        print(f"BPM: {new_bpm}")
        self.bpm = new_bpm
        self._update_interval(new_bpm)

    def get_time(self):
        if self.is_on:
            now = int(round(time.time() * 1000))%self.note_length

            if(now)<self.last_time:
                if self.metronome_seq_lumbuel[self.current_note]:
                    self.sound.play(block=False)
                self.current_note = ((self.current_note+1)%self.max_notes)
            self.last_time = now

