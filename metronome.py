import time
from soundy_pygame import Soundy

class Metronome:
    def __init__(self, bpm=120, path=None):
        self.is_on = False
        self.bpm = bpm
        self.bpm_interval_ms = int(60/self.bpm*1000)
        self.last_time = 0
        self.sound = Soundy(path)

    def _update_interval(self, new_bpm):
        self.bpm_interval_ms = int(60/new_bpm*1000)

    def switch(self):
        self.is_on = not self.is_on


    def set_bpm(self,input):
        self.wait = True
        new_bpm = 10+input*300
        print(f"BPM: {new_bpm}")
        self.bpm = new_bpm
        self._update_interval(new_bpm)

    def get_time(self):
        if self.is_on:
            now = int(round(time.time() * 1000))%self.bpm_interval_ms
            if(now)<self.last_time:
                self.sound.play(block=False)
            self.last_time = now
