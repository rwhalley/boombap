import time
from soundy_pygame import Soundy
from pathlib import Path
from os import listdir
from os.path import isfile, join


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
        self.offset = 0
        self.current_beat = 0
        self.sound = Soundy(path)
        self.mbungmbung_path = str(Path(__file__).parent / 'samples/')+'/2/'
        self.col_path = str(Path(__file__).parent / 'samples/')+'/1/'
        self.nder_path = str(Path(__file__).parent / 'samples/')+'/0/'
        self.accompaniment_paths = [self.mbungmbung_path,self.col_path]
        self.accompaniment_sounds = self._load_sounds()
        self.mbungmbung_volume = 128
        self.col_volume = 128
        self.kaolack = [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0]

        self.kaolack_accompaniment =   [[[1,0,0,0,0,1,0,0,1,0,0,0,0,2,0,0],  # pax
                                         [0,0,0,1,0,0,0,0,0,0,0,1,1,0,0,0],  # gin
                                         [0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1],  # tan
                                         [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], # tet

                                        [[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],  # pax 4
                                         [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],  # gin 0
                                         [0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                         [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],  # tan 2
                                         [0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0]]] # tet 3

        self.lumbuel = [1,0,0,0,1,0,1,0,0,1,0,0]
        self.lumbuel_accompaniment = [[[0,0,0,0,1,0,0,0,0,0,1,0],
                                       [0,0,1,0,0,0,0,0,1,0,0,0],
                                       [1,1,0,0,0,1,1,1,0,0,0,1],
                                       [0,0,0,0,0,0,0,0,0,0,0,0]],

                                      [[0,0,0,0,0,0,0,0,0,0,0,0],
                                       [1,0,0,0,0,0,1,0,0,0,0,0],
                                       [0,0,0,0,0,0,0,0,0,0,0,0],
                                       [0,0,0,0,0,1,0,0,0,0,0,1],
                                       [0,1,0,1,0,0,0,1,0,1,0,0]]]
        self.njouk = [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0]
        self.njouk_accompaniment = [[[0,0,0,0,0,0,1,0,0,1,0,0,0,0,1,0],  # pax
                                     [1,0,0,1,0,0,0,0,1,0,0,1,0,0,0,0],  # gin
                                     [0,0,1,0,1,0,0,1,0,0,1,0,1,0,0,1],  # tan
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], # tet

                                    [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax 4
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gin 0
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # tan 2
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]] # tet 3


        self.nothing=              [[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax 4
                                     [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],  # gin 0
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                     [0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1],  # tan 2
                                     [0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0]]] # tet 3
        self.metronome_seq = self.kaolack
        self.accompaniment = self.kaolack_accompaniment


    def _load_sounds(self):

        paths = self.accompaniment_paths
        all_sounds = []
        for path in paths:
            sounds = []
            onlyfiles = [f for f in sorted(listdir(path)) if isfile(join(path, f))]
            for file in onlyfiles:
                if file.endswith('.wav'):
                    if file.startswith('.'):
                        pass
                    else:
                        sounds.append(Soundy(path+file))
            for sound in sounds:
                sound.remove_artifacts()
                sound.normalize()
                sound.make_loud()
            all_sounds.append(sounds)
        return all_sounds

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
        self.is_on = (self.is_on + 1) % 4
        if self.is_on == 1:
            print("KAOLACK")
            self.metronome_seq = self.kaolack
            self.accompaniment=self.kaolack_accompaniment
            self._update_meter(4)
        elif self.is_on == 2:
            print("LUMBUEL")
            self.metronome_seq = self.lumbuel
            self.accompaniment = self.lumbuel_accompaniment
            self._update_meter(3)
        elif self.is_on == 3:
            print("NJOUK")
            self.metronome_seq = self.njouk
            self.accompaniment = self.njouk_accompaniment
            self._update_meter(4)
        else:
            self._update_meter(4)


    def update_volume(self,drum,volume):
        for sound in self.accompaniment_sounds[drum]:
            sound.set_volume(volume)

    def set_bpm(self,input):
        self.wait = True
        new_bpm = 40+input*200
        print(f"BPM: {new_bpm}")
        self.bpm = new_bpm
        self._update_interval(new_bpm)

    def get_time(self):
        if self.is_on:
            now = int(round(time.time() * 1000))%(self.note_length + self.offset)
            print(now)

            if(now)<self.last_time:
                try:
                    #print(len(self.accompaniment))
                    for i,drum in enumerate(self.accompaniment):
                        #print(drum)
                        for j,seq in enumerate(drum):
                            if seq[self.current_note] == 2:  # grace note
                                if not self.offset:
                                    self.offset = 0.25*self.note_length
                                    return
                                else:
                                    pass
                            if seq[self.current_note] and i==0:  # mbung mbung
                                if (j==0):
                                    self.accompaniment_sounds[i][0].play(block=False)
                                if (j==1):
                                    self.accompaniment_sounds[i][4].play(block=False)
                                if (j==2):
                                    self.accompaniment_sounds[i][2].play(block=False)
                                if (j==3):
                                    self.accompaniment_sounds[i][3].play(block=False)
                            if seq[self.current_note] and i==1:  # col
                                if (j==0):
                                    self.accompaniment_sounds[i][4].play(block=False)
                                if (j==1):
                                    self.accompaniment_sounds[i][0].play(block=False)
                                if (j==2):
                                    self.accompaniment_sounds[i][1].play(block=False)
                                if (j==3):
                                    self.accompaniment_sounds[i][2].play(block=False)
                                if (j==4):
                                    self.accompaniment_sounds[i][3].play(block=False)
                            self.offset = 0

                    if self.metronome_seq[self.current_note]:
                        self.sound.play(block=False)
                except:
                    pass
                self.current_note = ((self.current_note+1)%self.max_notes)
            self.last_time = now

