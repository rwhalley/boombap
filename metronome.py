import time
from soundy_pygame import Soundy
from pathlib import Path
from os import listdir
from os.path import isfile, join
import threading
from midiout import MIDIPlayer
from midi_recorder import MIDIRecorder
import sabar_rhythms as sr


class Metronome:
    def __init__(self,bpm=100, path=None, controller=None):
        self.is_on = False
        self.bpm = bpm
        self.beat_length = int(60 / self.bpm * 1000)
        self.max_beats = 4

        # --- for looper ---
        self.beats_per_bar = 8
        self.current_loop_beat = 0
        self.notes_per_beat = 4
        self.notes_per_bar = self.notes_per_beat*self.beats_per_bar
        self.bars_per_loop = 4
        # --- end for looper ---

        self.max_notes = self.max_beats * self.notes_per_beat
        self.measure_length = int(self.beat_length * 4)
        self.note_length = int(self.beat_length / 4)
        self.last_time = 0
        self.last_ts = 0
        self.current_note = 0
        self.current_grace_note = 0

        self.offset = 0
        self.current_beat = 0
        self.sound = Soundy(path)
        self.grace_note_active = -1
        self.col_grace_seq = -1
        self.grace_played = False
        self.grace_BPM_thresh = 160
        self.mbungmbung_path = str(Path(__file__).parent / 'accompaniment/')+'/mbalax1/'
        self.mbalax2_path = str(Path(__file__).parent / 'accompaniment/')+'/mbalax2/'
        self.talmbat_path = str(Path(__file__).parent / 'accompaniment/')+'/talmbat/'
        self.tulli_path = str(Path(__file__).parent / 'accompaniment/')+'/tulli/'
        self.tugone_path = str(Path(__file__).parent / 'accompaniment/')+'/tugone1/'
        self.tugone2_path = str(Path(__file__).parent / 'accompaniment/')+'/tugone2/'
        self.nder_path = str(Path(__file__).parent / 'accompaniment/')+'/Nder/'
        self.drums = ["Nder","mbalax1","talmbat","tulli","tugone1","tugone2","mbalax2"]
        self.drum_hits = ["pax","pin","gin","rwan","tan","tet","drin","cex","cek"]
        self.accompaniment_paths = [self.mbungmbung_path,self.mbalax2_path,self.talmbat_path,self.tulli_path,self.tugone_path,self.tugone2_path]
        self.accompaniment_sounds = self._load_sounds()
        self.mbungmbung_volume = 0 #128
        self.col_volume = 0 #128

        self.metronome_seq = sr.meters["kaolack"]  # initialization
        self.accompaniment = sr.rhythms["kaolack"] # initialization

        self.midi_player = None
        self.midi_recorder = None
        self.midi_player = None
        self.midi_recorder = None
        self.loop_blacklist = []
        self.last_pos = 0
        self.controller = controller




    def _load_sounds(self):

        paths = self.accompaniment_paths
        all_sounds = {}
        for path in paths:
            sounds = {}
            onlyfiles = [f for f in sorted(listdir(path)) if isfile(join(path, f))]
            for file in onlyfiles:
                if file.endswith('.wav'):
                    if file.startswith('.'):
                        pass
                    else:
                        sounds[self.get_hit_from_filename(file)] = Soundy(path+file)

                        #sounds.append(Soundy(path+file))
            for key, sound in sounds.items():
                sound.remove_artifacts()
                sound.normalize()
                sound.make_loud()
            all_sounds[self.get_drum_from_filename(path)] = sounds
        return all_sounds

    def get_drum_from_filename(self,path):
        for drum in self.drums:
            if drum in path:
                return drum

    def get_hit_from_filename(self,filename):
        for hit in self.drum_hits:
            if hit in filename:
                return hit

    def get_notes_per_loop(self):
        return self.notes_per_bar*self.bars_per_loop

    def set_bars_per_loop(self,num):
        self.bars_per_loop = num

    def _update_interval(self, new_bpm):
        self.beat_length = int(60 / new_bpm * 1000)
        self.measure_length = int(self.beat_length * self.beats_per_bar)
        self.note_length = int(self.beat_length /  4)

    def _update_meter(self,notes_per_beat):
        self.notes_per_beat = notes_per_beat
        self.max_notes = self.max_beats * self.notes_per_beat
        self.measure_length = int(self.beat_length * 4)
        self.note_length = int(self.beat_length / 4)


    def switch(self,i):
        print(f"i: {i}")
        if i> len(sr.button_order)-1:
            return None
        id = sr.button_order[i]
        print(f"id: {id}")
        # print(sr.meters[sr.button_order[i]])
        # print(sr.rhythms[sr.button_order[i]])
        # print(sr.rhythms['thieboudjeun'])
        # print("WHAT")

        if id != "empty":
            #self.is_on = False
            #time.sleep(0.1)

            self.metronome_seq = sr.meters[sr.button_order[i]]
            self.accompaniment = sr.rhythms[sr.button_order[i]]
            self.midi_recorder.clear_all_loops()

            # if (len(self.metronome_seq) % 3) == 0:
            #     self._update_meter(3)
            # else:
            #     self._update_meter(4)

            self.notes_per_beat = sr.objects[i].notes_per_beat
            self.beats_per_bar = sr.objects[i].beats_per_bar
            self.notes_per_bar = self.notes_per_beat*self.beats_per_bar

            self.max_notes = self.max_beats * self.notes_per_beat
            self.measure_length = int(self.beat_length * self.beats_per_bar)
            self.note_length = int(self.beat_length / self.notes_per_beat)
            self.current_note = 0
            self.current_grace_note = 0
            self.offset = 0
            self.current_beat = 0


            self.is_on = True


        else:
            self.is_on = False


    def update_volume(self,drum,volume):
        for sound in self.accompaniment_sounds[drum]:
            sound.set_volume(volume)

    def set_bpm(self,input):
        new_bpm = 40+input*200
        print(f"BPM: {new_bpm}")
        self.bpm = new_bpm
        self._update_interval(new_bpm)

    def bpm_up(self):
        self.bpm = self.bpm + 10
        self._update_interval(self.bpm)

    def bpm_down(self):
        if self.bpm > 10:
            self.bpm = self.bpm - 10
            self._update_interval(self.bpm)


    def play_accompaniment(self, state):
        for i, (drum_key, drum_value) in enumerate(self.accompaniment.items()): # for each drum in accompaniment
            if drum_value.drum:
                for j, (hit_key, hit_value) in enumerate (drum_value.drum.items()): # for each type of hit in drum
                    if hit_value and hit_value[self.current_note] == 2 and state != 2:
                        self.grace_note_active = True
                    elif hit_value and hit_value[self.current_note-1] == 2 and state == 2:
                        #self.accompaniment_sounds[drum_key][hit_key].set_volume_stereo(drum_value.volume_left, drum_value.volume_right)
                        self.accompaniment_sounds[drum_key][hit_key].play(block=False)
                        self.grace_note_active = False
                    elif hit_value and hit_value[self.current_note] == 1 and state == 1:
                        for j, (shit_key, shit_value) in enumerate (drum_value.drum.items()): # iterate through hits and
                                if shit_value:
                                    self.accompaniment_sounds[drum_key][shit_key].stop() # stop any other sounds playing
                        self.accompaniment_sounds[drum_key][hit_key].play(block=False, lvol= drum_value.lvol, rvol = drum_value.rvol)
                        #self.accompaniment_sounds[drum_key][hit_key].play(block=False)


    # def play_accompaniment_old(self, state):
    #     for i,drum in enumerate(self.accompaniment):
    #         for j,seq in enumerate(drum):
    #             place = seq[self.current_note]
    #
    #             ### MBUNG MBUNG ###
    #             if place == 2 and i ==0 and self.bpm<self.grace_BPM_thresh:
    #                 self.grace_note_active = j
    #
    #             ### COL ###
    #             if place == 2 and i ==1 and self.bpm<self.grace_BPM_thresh:
    #                 self.col_grace_seq = j
    #
    #             ### MBUNG MBUNG ###
    #             if i==0:
    #                 if (state=="normal" and j == self.grace_note_active):
    #                     #print("SKIP MBUNG")
    #                     pass
    #                 elif(state == "normal" and place != 0 and j != self.grace_note_active):
    #                     #print("PLAY NOTES")
    #                     for sound in self.accompaniment_sounds[i]:
    #                         sound.stop()
    #                     if (j==0):
    #                         self.accompaniment_sounds[i][0].play(block=False)
    #                     if (j==1):
    #                         self.accompaniment_sounds[i][4].play(block=False)
    #                     if (j==2):
    #                         self.accompaniment_sounds[i][2].play(block=False)
    #                     if (j==3):
    #                         self.accompaniment_sounds[i][3].play(block=False)
    #
    #                 elif (state=="grace" and i==0 and j==self.grace_note_active):
    #                     #print("PLAY GRACE NOTES")
    #                     for sound in self.accompaniment_sounds[i]:
    #                         sound.stop()
    #                     if (j==0):
    #                         self.accompaniment_sounds[i][0].play(block=False)
    #                     if (j==1):
    #                         self.accompaniment_sounds[i][4].play(block=False)
    #                     if (j==2):
    #                         self.accompaniment_sounds[i][2].play(block=False)
    #                     if (j==3):
    #                         self.accompaniment_sounds[i][3].play(block=False)
    #                     self.grace_note_active = -1
    #
    #             ### COL ###
    #             if i==1:
    #                 if (state=="normal" and j == self.col_grace_seq):
    #                     #print("SKIP COL")
    #                     pass
    #                 elif (state=="normal" and place != 0 and j != self.col_grace_seq):
    #                     #print("PLAY COL")
    #                     for sound in self.accompaniment_sounds[i]:
    #                         sound.stop()
    #                     if (j==0):
    #                         self.accompaniment_sounds[i][4].play(block=False)
    #                     if (j==1):
    #                         self.accompaniment_sounds[i][0].play(block=False)
    #                     if (j==2):
    #                         self.accompaniment_sounds[i][1].play(block=False)
    #                     if (j==3):
    #                         self.accompaniment_sounds[i][2].play(block=False)
    #                     if (j==4):
    #                         self.accompaniment_sounds[i][3].play(block=False)
    #
    #                 elif (state=="col_grace" and i==1 and j == self.col_grace_seq):
    #                     for sound in self.accompaniment_sounds[i]:
    #                         sound.stop()
    #                     if (j==0):
    #                         self.accompaniment_sounds[i][4].play(block=False)
    #                     if (j==1):
    #                         self.accompaniment_sounds[i][0].play(block=False)
    #                     if (j==2):
    #                         self.accompaniment_sounds[i][1].play(block=False)
    #                     if (j==3):
    #                         self.accompaniment_sounds[i][2].play(block=False)
    #                     if (j==4):
    #                         self.accompaniment_sounds[i][3].play(block=False)
    #                     self.col_grace_seq = -1
    #                     #print("PLAY COL GRACE")


    def get_position(self,timestamp=None):
        "Get float 0 to 1 that represents current position in bar."
        ts=None
        if timestamp:
            ts = timestamp
        else:
            ts = time.time()
        pos = 0
        normalizer = float(self.bars_per_loop*self.beats_per_bar*self.notes_per_beat)
        now = int(round(ts * 1000))%(self.note_length)
        micro_pos = now/float(self.note_length)
        pos = (self.current_loop_beat + micro_pos) / normalizer
        # print(f"micro_pos: {micro_pos}")
        # print(f"normalizer: {normalizer}")
        # print(f"current_beat: {self.current_loop_beat}")
        # print(f"pre_pos: {self.current_loop_beat + micro_pos}")
        # print(f"pos: {pos}")
        return pos

    # def get_time(self):
    #     ts = time.time()
    #     return ts

    # def midithingloop(self):
    #     ts = time.time()
    #     if self.metronome.is_on:
    #         note = self.metronome.get_note()
    #         if note:
    #             if (ts-note.when)<0.1: # don't play if note was just recorded
    #                 self.midi_player.play_note(note)
    #                 self.play_sound(note)

    # def get_note_alt(self,ts):
    #
    #     current_pos = self.get_position(timestamp=ts)
    #
    #     notes=[]
    #
    #     if (self.midi_recorder.my_loop):
    #
    #             for i, entry in enumerate(self.midi_recorder.my_loop):  # Go through all the notes in loop
    #                 if (current_pos > entry.bar_position) and not (i in self.loop_blacklist): # if it's time to play, play the entry, and add it to the blacklist for this measure
    #                     self.loop_blacklist.append(i)
    #                     notes.append(entry)
    #
    #
    #     if self.last_pos > 0.9 and current_pos < 0.1:  # loop has ended
    #         self.loop_blacklist = []  # clear loop blacklist
    #
    #     self.last_pos = current_pos
    #
    #     return notes

    def get_note(self,ts):


        current_pos = self.get_position(timestamp=ts)

        notes=[]

        if (self.midi_recorder.my_loop):

            entry = self.midi_recorder.my_loop[self.midi_recorder.current_loop_index]  # Go through all the notes in loop
            if (current_pos > entry.bar_position) and not (self.midi_recorder.current_loop_index in self.loop_blacklist): # if it's time to play, play the entry, and add it to the blacklist for this measure
                self.loop_blacklist.append(self.midi_recorder.current_loop_index)
                notes.append(entry)
                self.midi_recorder.current_loop_index+=1
                self.midi_recorder.current_loop_index = self.midi_recorder.current_loop_index%self.midi_recorder.current_loop_length


        if self.last_pos > 0.9 and current_pos < 0.1:  # loop has ended
            self.loop_blacklist = []  # clear loop blacklist

        self.last_pos = current_pos

        return notes


    def play_sequencer(self, ts):

        # When now = 0, play a note.
        now = int(round(ts * 1000))%(self.note_length)

        # Is it time to play a sequence note? Or a Grace note?
        normal = now < self.last_time
        grace = now > (int(0.50*self.note_length))

        self.last_time = now

        if grace and self.bpm<self.grace_BPM_thresh:
            if (self.grace_note_active == True) :
                self.play_accompaniment(2)


            # if (self.col_grace_seq >=0):
            #     self.play_accompaniment("col_grace")
            #     self.col_grace_seq = -1

        if normal:
            self.play_accompaniment(1)

            if self.metronome_seq[self.current_note]:
                    self.sound.play(block=False)

            self.current_note = ((self.current_note+1)%self.max_notes)
            self.current_loop_beat = ((self.current_loop_beat+1) %self.get_notes_per_loop())





    # def get_time_old(self):
    #
    #     # get current timestamp
    #     ts = time.time()
    #
    #     # if metronome is on
    #     if self.is_on:
    #
    #         ### For Accompaniment
    #
    #         # is_time_to_play_seq_note()
    #         # is_time_to_play_grace_note()
    #
    #         # When now = 0, play a note.
    #         now = int(round(ts * 1000))%(self.note_length)
    #
    #         # Is it time to play a sequence note? Or a Grace note?
    #         normal = now < self.last_time
    #         grace = now > (int(0.50*self.note_length))
    #
    #         ### --- MIDI LOoPER ---
    #         #get_current_position_in_bar()
    #         current_pos = self.get_position(timestamp=ts)
    #
    #         ### -- QUNEO LOOP ---
    #         if(len(self.midi_recorder.my_loop)>0):  # If there are notes to loop
    #             midis = []
    #             banks = []
    #             ports = []
    #             when_addeds = []
    #             for i, entry in enumerate(self.midi_recorder.my_loop):  # Go through all the notes in loop
    #                 midi = entry[1]
    #                 entry_pos = entry[0]
    #                 bank = entry[2]
    #                 port = entry[3]
    #                 when_added = entry[4]
    #                 # print(when_added)
    #                 # print(f"midi {midi}")
    #                 # print(f"entry pos {entry_pos}")
    #                 # print(f"bank {bank}")
    #                 # print(f"port {port}")
    #
    #                 if (current_pos > entry_pos) and not (i in self.loop_blacklist): # if it's time to play, play the entry, and add it to the blacklist for this measure
    #                     #print("WOO")
    #                     midis.append(midi)
    #                     banks.append(bank)
    #                     ports.append(port)
    #                     when_addeds.append(when_added)
    #                     self.loop_blacklist.append(i)
    #
    #                     print("DOUBLE OK")
    #                     #print(time.time() - when_addeds[0])
    #
    #                     if (ts - when_addeds[0]) > 0.1: #if time has passed
    #                         self.controller.play_sound(midis,False,banks,ports)
    #                         self.midi_player.play_note(midis,ports)
    #
    #
    #             if self.last_pos > 0.9 and current_pos < 0.1:  # loop has ended
    #                 self.loop_blacklist = []  # clear loop blacklist
    #
    #         self.last_pos = current_pos
    #
    #         # --- End MIDI looper ---
    #
    #
    #
    #         # --- ACCOMPANIMENT ----
    #
    #         if normal:
    #             if self.metronome_seq[self.current_note]:
    #                     self.sound.play(block=False)
    #         if True:
    #             if self.bpm<self.grace_BPM_thresh:
    #                 if (grace and self.grace_note_active) :
    #                     #print("Grace")
    #
    #                     self.play_accompaniment(2)
    #                     #self.grace_note_active = -1
    #
    #                 # if (grace and self.col_grace_seq >=0):
    #                 #     #print("Col Grace")
    #                 #     self.play_accompaniment("col_grace")
    #                 #
    #                 #     self.col_grace_seq = -1
    #
    #
    #             ### Metronome ###
    #             if self.bpm<self.grace_BPM_thresh:
    #                 if normal and not self.grace_note_active:
    #                     self.play_accompaniment(1)
    #             else:
    #                 if normal:
    #                     self.play_accompaniment(1)
    #
    #         if normal:
    #
    #             self.current_note = ((self.current_note+1)%self.max_notes)
    #
    #             #print(self.notes_per_bar)
    #             self.current_loop_beat = ((self.current_loop_beat+1) %self.get_notes_per_loop())
    #             #print(f"CURRENT NOTE: {self.current_note}")
    #             #print(f"CURRENT_LOOP_NOTE: {self.current_loop_beat}")
    #
    #         self.last_time = now




