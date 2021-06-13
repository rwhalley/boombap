import time
from soundy_pygame import Soundy

class Metronome:
    def __init__(self, bpm=120, path=None):
        self.is_on = False
        self.bpm = bpm
        self.beat_length = int(60 / self.bpm * 1000)
        self.max_beats = 4
        self.notes_per_beat = 4
        self.max_notes = self.max_beats * self.notes_per_beat
        self.measure_length = int(self.beat_length * 4)
        self.note_length = int(self.beat_length / 4)
        self.last_time = 0
        self.current_note = 0
        self.current_beat = 0
        self.sound = Soundy(path)
        self.kaolack = [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0]
        self.lumbuel = [1,0,0,0,1,0,1,0,0,1,0,0]
        self.metronome_seq = self.kaolack


    def _update_interval(self, new_bpm):
        self.beat_length = int(60 / new_bpm * 1000)
        self.measure_length = int(self.beat_length * 4)
        self.note_length = int(self.beat_length / 4)

    def _update_meter(self,notes_per_beat):
        self.notes_per_beat = notes_per_beat
        self.max_notes = self.max_beats * self.notes_per_beat
        self.measure_length = int(self.beat_length * 4)
        self.note_length = int(self.beat_length / 4)


    def switch(self):
        self.is_on = (self.is_on + 1) % 3
        if self.is_on == 1:
            self.metronome_seq = self.kaolack
            self._update_meter(4)
        elif self.is_on == 2:
            self.metronome_seq = self.lumbuel
            self._update_meter(3)




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
                if self.metronome_seq[self.current_note]:
                    self.sound.play(block=False)
                self.current_note = ((self.current_note+1)%self.max_notes)
            self.last_time = now

