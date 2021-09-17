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
        # --- end for looper ---

        self.max_notes = self.max_beats * self.notes_per_beat
        self.measure_length = int(self.beat_length * 4)
        self.note_length = int(self.beat_length / 4)
        self.last_time = 0
        self.current_note = 0
        self.current_grace_note = 0
        self.offset = 0
        self.current_beat = 0
        self.sound = Soundy(path)
        self.grace_note_active = -1
        self.col_grace_seq = -1
        self.grace_played = False
        self.grace_BPM_thresh = 160
        self.mbungmbung_path = str(Path(__file__).parent / 'samples/')+'/2/'
        self.col_path = str(Path(__file__).parent / 'samples/')+'/1/'
        self.nder_path = str(Path(__file__).parent / 'samples/')+'/0/'
        self.accompaniment_paths = [self.mbungmbung_path,self.col_path]
        self.accompaniment_sounds = self._load_sounds()
        self.mbungmbung_volume = 0 #128
        self.col_volume = 0 #128

        self.metronome_seq = sr.meters["kaolack"]  # initialization
        self.accompaniment = sr.rhythms["kaolack"] # initialization

        self.midi_player = None
        self.midi_recorder = None
        self.midi_player = MIDIPlayer()
        print("START MIDIPLAYER")
        self.midi_recorder = MIDIRecorder(self)
        print("START RECORDER")
        self.loop_whitelist = []
        self.last_pos = 0
        self.controller = controller




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


    def switch(self,i):
        print(f"i: {i}")
        id = sr.button_order[i]
        print(f"id: {id}")
        # print(sr.meters[sr.button_order[i]])
        # print(sr.rhythms[sr.button_order[i]])
        # print(sr.rhythms['thieboudjeun'])
        # print("WHAT")

        if id != "empty":
            self.is_on = True
            self.metronome_seq = sr.meters[sr.button_order[i]]
            self.accompaniment = sr.rhythms[sr.button_order[i]]
            if (len(self.metronome_seq) % 3) == 0:
                self._update_meter(3)
            else:
                self._update_meter(4)
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
        for i,drum in enumerate(self.accompaniment):
            for j,seq in enumerate(drum):
                place = seq[self.current_note]

                ### MBUNG MBUNG ###
                if place == 2 and i ==0 and self.bpm<self.grace_BPM_thresh:
                    self.grace_note_active = j

                ### COL ###
                if place == 2 and i ==1 and self.bpm<self.grace_BPM_thresh:
                    self.col_grace_seq = j

                ### MBUNG MBUNG ###
                if i==0:
                    if (state=="normal" and j == self.grace_note_active):
                        #print("SKIP MBUNG")
                        pass
                    elif(state == "normal" and place != 0 and j != self.grace_note_active):
                        #print("PLAY NOTES")
                        for sound in self.accompaniment_sounds[i]:
                            sound.stop()
                        if (j==0):
                            self.accompaniment_sounds[i][0].play(block=False)
                        if (j==1):
                            self.accompaniment_sounds[i][4].play(block=False)
                        if (j==2):
                            self.accompaniment_sounds[i][2].play(block=False)
                        if (j==3):
                            self.accompaniment_sounds[i][3].play(block=False)

                    elif (state=="grace" and i==0 and j==self.grace_note_active):
                        #print("PLAY GRACE NOTES")
                        for sound in self.accompaniment_sounds[i]:
                            sound.stop()
                        if (j==0):
                            self.accompaniment_sounds[i][0].play(block=False)
                        if (j==1):
                            self.accompaniment_sounds[i][4].play(block=False)
                        if (j==2):
                            self.accompaniment_sounds[i][2].play(block=False)
                        if (j==3):
                            self.accompaniment_sounds[i][3].play(block=False)
                        self.grace_note_active = -1

                ### COL ###
                if i==1:
                    if (state=="normal" and j == self.col_grace_seq):
                        #print("SKIP COL")
                        pass
                    elif (state=="normal" and place != 0 and j != self.col_grace_seq):
                        #print("PLAY COL")
                        for sound in self.accompaniment_sounds[i]:
                            sound.stop()
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

                    elif (state=="col_grace" and i==1 and j == self.col_grace_seq):
                        for sound in self.accompaniment_sounds[i]:
                            sound.stop()
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
                        self.col_grace_seq = -1
                        #print("PLAY COL GRACE")


    def get_position(self):
        "Get float 0 to 1 that represents current position in bar."
        pos = 0
        normalizer = float(self.beats_per_bar*self.notes_per_beat)
        now = int(round(time.time() * 1000))%(self.note_length)
        micro_pos = now/float(self.note_length)
        pos = (self.current_loop_beat + micro_pos) / normalizer
        # print(f"micro_pos: {micro_pos}")
        # print(f"normalizer: {normalizer}")
        # print(f"current_beat: {self.current_loop_beat}")
        # print(f"pre_pos: {self.current_loop_beat + micro_pos}")
        # print(f"pos: {pos}")
        #if self.current_loop_beat > 30:
        #    print("WHATTSSGSTRDSDFGSD")
        return pos

    def get_time(self):
        try:
            if self.is_on:
                now = int(round(time.time() * 1000))%(self.note_length)
                normal = now < self.last_time
                grace = now > (int(0.50*self.note_length))

                ### --- MIDI LOoPER ---
                current_pos = self.get_position()

                ### -- QUNEO LOOP ---
                if(len(self.midi_recorder.my_loop)>0):
                    #print(f"current pos {current_pos}")
                    midis = []
                    banks = []
                    ports = []
                    when_addeds = []
                    for i, entry in enumerate(self.midi_recorder.my_loop):
                        midi = entry[1]
                        entry_pos = entry[0]
                        bank = entry[2]
                        port = entry[3]
                        when_added = entry[4]
                        # print(when_added)
                        # print(f"midi {midi}")
                        # print(f"entry pos {entry_pos}")
                        # print(f"bank {bank}")
                        # print(f"port {port}")

                        if (current_pos > entry_pos) and not (i in self.loop_whitelist):
                            #print("WOO")
                            midis.append(midi)
                            banks.append(bank)
                            ports.append(port)
                            when_addeds.append(when_added)
                            self.loop_whitelist.append(i)


                    self.midi_player.play_note(midis,ports)
                    self.controller.play_sound(midis,False,banks,ports)


#                     try:
#                         if(time.time() - when_addeds[0]) > 0.1:
#                             #if "reface CP" in ports:
# #                            self.midi_player.play_note(midis)
#                             # elif len(ports) == 0:
#                             #     pass
#                             # else:
#                             #     pass #self.controller.play_sound(midis,False,banks)
#                     except:
#                         pass






                    # if len(midis) > 0:
                    #     print("MIDIS")
                    #     print(midis)
                    #     print(ports)
                    # #if ("QUNEO" in ports):
                    # #    self.controller.play_sound(midis,False,banks)
                    # #    print("PLAY QNUENO")
                    # if ("reface CP" in ports):
                    #     print("PLAY CP")

                          # ---- PLAY NOTE HERE SOMEHOW ---


                    if self.last_pos > 0.9 and current_pos < 0.1:  # loop has ended
                        #print(f"current_pos {current_pos}")
                        #print(f"last pos {self.last_pos}")
                        #print("ENDLOOP")
                        self.loop_whitelist = []  # clear loop whitelist
                self.last_pos = current_pos

                # --- End MIDI looper ---


                if normal:
                    if self.metronome_seq[self.current_note]:
                            self.sound.play(block=False)
                if True:
                    if self.bpm<self.grace_BPM_thresh:
                        if (grace and self.grace_note_active>=0) :
                            #print("Grace")

                            self.play_accompaniment("grace")
                            self.grace_note_active = -1

                        if (grace and self.col_grace_seq >=0):
                            #print("Col Grace")
                            self.play_accompaniment("col_grace")

                            self.col_grace_seq = -1


                    ### Metronome ###
                    if self.bpm<self.grace_BPM_thresh:
                        if normal and not self.grace_note_active>=0:
                            self.play_accompaniment("normal")
                    else:
                        if normal:
                            self.play_accompaniment("normal")

                if normal:

                    self.current_note = ((self.current_note+1)%self.max_notes)
                    self.current_loop_beat = ((self.current_loop_beat+1) %self.notes_per_bar)
                    #print(f"CURRENT NOTE: {self.current_note}")
                    #print(f"CURRENT_LOOP_NOTE: {self.current_loop_beat}")

                self.last_time = now
        except:
            pass



