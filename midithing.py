#!/usr/bin/python

import time
import os
from os import listdir
from os.path import isfile, join, exists
import sys
from pathlib import Path
from threading import Thread
import pickle as p
from dataclasses import dataclass

import mido

from soundy_pygame import Soundy
from metronome import Metronome
import QUNEO
from midiout import MIDIPlayer
from midi_recorder import MIDIRecorder
from recorder import AudioRecorder
from slicer import Slicer
import CONFIG as c
import note
from page  import Kit, Page


class MidiControl:

    def __init__(self):

        self.basepath = '/Volumes/SQUIRREL/Kits/' # str(Path(__file__).parent / 'samples/')+'/'
        self.save_path = 'sound_data.pkl'
        self.current_bank = 0
        self.current_page = 0
        self.max_sample_length_seconds = 3
        self.max_page_size = 16
        self.max_bank_size = 16
        self.button = QUNEO
        self.VOL_SENS = False
        self.port_name = None
        self.ports = []
        self.semitone = .059463094359
        self.last_note = 1101001
        self.NON_LOOP = -2

        # -- Sound Data ---
        self.all_sounds = None
        self.all_sound_data = None

        # --- Shift Button States ---
        self.is_metronome_pressed = False
        self.is_loop_loader_pressed = False
        self.is_loop_saver_pressed = False
        self.is_bank_shift_pressed = False
        self.is_mode_shift_pressed = False
        self.is_page_shift_pressed = False
        self.is_loop_activator_shift_pressed = False
        self.on_notes = []

        self.devices = [] # QUNEO, Reface CP
        self.messages = []
        self.threads = []
        self.control_msgs = []
        self.devices = list(set(mido.get_input_names()))
        print(self.devices)

        # LOAD SAMPLES - Try Fast Load
        if exists(self.save_path):
            self.load_all_sound_data()
        else:
            self.load_all_samples()
            self.save_all_sound_data()

        # AUDIO RECORDER
        self.sample_recording_length_in_seconds = 5

        # START METRONOME
        self.metronome_path = Path(__file__).parent.resolve() / 'metronome/metronome.wav'
        self.metronome = Metronome(bpm=120,path=self.metronome_path, controller=self)

        self.last_ts = 0

        ## LOAD MIDI THREADS FOR TWO DEVICES

        self.midoports = []
        t1 = None
        t2 = None
        for device in self.devices:
            if "Midi Through" in device:
                pass
            elif c.SYNTH in device:
                #self.open_input(device,self.add_message)
                print(f"{c.SYNTH} synth found")
                #t1 = Thread(target=self.open_input, args=(device,self.add_message))
                c.MY_DEVICES[1] = device
                c.SYNTH = device
                #t1.start()
                self.midoports.append(mido.open_input(device))

            elif c.MIDI_CONTROLLER in device:
                print(f"{c.MIDI_CONTROLLER} midi controller found")
                #self.open_input(device,self.add_message)

                #t2 = Thread(target=self.open_input, args=(device,self.add_message))
                c.MY_DEVICES[0] = device
                c.MIDI_CONTROLLER = device
                #t2.start()
                self.midoports.append(mido.open_input(device))



        # START MIDI Player
        #self.metronome.midi_player = MIDIPlayer(self.devices)
        self.midi_player = MIDIPlayer(self.devices)

        # START MIDI RECORDER
        self.metronome.midi_recorder = MIDIRecorder(self.metronome)


        print("LOADING COMPLETE - STARTING MAIN LOOP")

        # MAIN LOOP FOR PROCESSING MIDI INPUT
        while True:

            #time.sleep(0.0002) # Reduce number of unnecessary cycles

            for port in self.midoports:
                self.add_message(port.poll())

            # IF METRONOME BUTTON TURNED ON
            if self.metronome.is_on:

                ts = time.time()
                # RUN LOOPER
                notes = self.metronome.get_note(ts)
                if notes:
                    for note in notes:
                        if (ts-note.when)>0.1: # don't play if note was just recorded
                            if note.port in c.SYNTH:
                                self.midi_player.play_note(note)
                            if note.port in c.MIDI_CONTROLLER:
                                if note.midi.type == "note_on":
                                    self.play_sound(note)
                                if note.midi.type == "note_off":
                                    if note.page > 0:
                                        self.cutoff_current_sound(note)

                # RUN ACCOMPANIMENT

                self.metronome.play_sequencer(ts)

            # PROCESS INPUT MIDI

            if self.messages:
                self.print_general_message(self.messages.pop(0))




    # MIDI INPUT CALLBACK
    def open_input(self,device,func):
        mido.open_input(device, callback=func)

    # ADD MIDI MESSAGE TO PROCESS QUEUE
    def add_message(self,midi):
        if midi:
            self.messages.append(midi)

    # Filter out unnecessary change control messages
    def print_general_message(self,midi):
        now = time.time()
        if midi.type == 'note_on' or midi.type == 'note_off':
            if midi.channel == c.MIDI_CONTROLLER_CHANNEL:
                self.sort_midi(midi,c.MIDI_CONTROLLER,now)
            elif midi.channel == c.SYNTH_MIDI_CHANNEL:
                self.sort_midi(midi,c.SYNTH,now)
        # elif midi.type == 'control_change':
        #    self.control_msgs.append(midi)
        # if midi.type == 'note_off' and len(self.control_msgs) >1:
        #     msg = self.control_msgs[-2]
        #     self.control_msgs = []
        #     if msg.channel == c.MIDI_CONTROLLER_CHANNEL:
        #         self.sort_midi(msg,c.MIDI_CONTROLLER,now)


# SAMPLE LOADING

    def reload_bank(self,bank_num):
        new_bank = []
        path = self.basepath+str(bank_num)+'/'
        onlyfiles = [f for f in sorted(listdir(path)) if isfile(join(path, f))]
        for file in onlyfiles:
            if file.endswith('.wav'):
                if file.startswith('.'):
                    pass
                else:
                    new_bank.append(Soundy(path+file))
        try:
            self.all_sounds[self.current_page].kits[bank_num] = new_bank
        except IndexError:
            self.all_sounds[self.current_page].append(new_bank)
        self.pre_process_sounds(sounds = self.all_sounds[self.current_page].kits[bank_num])

    def load_all_sound_data(self):
        print("# Loading Sound Data from Pickle")
        self.all_pages = p.load(open("sound_data.pkl",'rb'))
        self.all_sounds = []

        for i, page in enumerate(self.all_pages):

            newpage = Page("","",[])
            for j, kit in enumerate(page.kits):
                newkit = Kit("","",[])
                for k, sound_arr in enumerate(kit.samples):

                    newkit.samples.append(Soundy(fast_load=True, arr=sound_arr))
                newpage.kits.append(newkit)
            self.all_sounds.append(newpage)
        print("# Sound Data Loaded from Pickle")


    def save_all_sound_data(self):
        print("# Saving Sound Data to Pickle")
        self.all_pages = []
        for i, page in enumerate(self.all_sounds):
            newpage = Page("","",[])
            for j, kit in enumerate(page.kits):

                newkit = Kit("","",[])
                for sound in kit.samples:
                    newkit.samples.append(sound.get_original_sound_array())
                newpage.kits.append(newkit)
            self.all_pages.append(newpage)
        p.dump(self.all_pages, open('sound_data.pkl','wb'))
        self.all_pages = None
        print("# Sound Data Saved to Pickle")





    def get_immediate_subdirectories(self,a_dir):
        return [name for name in os.listdir(a_dir)
                if os.path.isdir(os.path.join(a_dir, name))]

    def get_all_kit_dirs(self,path):
        output = []
        for dir in sorted(self.get_immediate_subdirectories(path)):
            output.append(sorted(self.get_immediate_subdirectories(path+'/'+dir+'/')))
        return output

    def load_all_samples(self):
        pages = (sorted(self.get_immediate_subdirectories(self.basepath)))
        kits_names = self.get_all_kit_dirs(self.basepath)
        self.all_sounds = []
        for i, page in enumerate(pages):
            kits = []
            for kit_name in kits_names[i]:
                kit = Kit(kit_name,self.basepath+'/'+page+'/'+kit_name+'/',[])
                samples = [f for f in sorted(listdir(kit.path)) if isfile(join(kit.path, f))]
                for file in samples:
                    if file.endswith('.wav'):
                        if file.startswith('.'):
                            pass
                        else:
                            kit.samples.append(Soundy(kit.path+file))

                kits.append(kit)

            self.all_sounds.append(Page(page,self.basepath+'/'+page+'/',kits))
            print(self.all_sounds)


    def load_all_samples_old(self):
        print("# Loading All Samples from File")
        self.all_sounds = []
        if c.PI_FAST_LOAD:
            max = 1
        else:
            max = 32
        for i in range(0,max): #  Load first 32 banks only
            try:
                bank = []
                path = self.basepath + str(i)+'/'
                onlyfiles = [f for f in sorted(listdir(path)) if isfile(join(path, f))]
                for file in onlyfiles:
                    if file.endswith('.wav'):
                        if file.startswith('.'):
                            pass
                        else:
                            bank.append(Soundy(path+file))
                self.all_sounds[self.current_page].append(bank)
            except FileNotFoundError:
                #print("less than 8 sample banks found")
                pass
        for bank in self.all_sounds:
            if c.PI_FAST_LOAD:
                print("PI FAST LOAD ACTIVE")
            else:
                self.pre_process_sounds(sounds = bank)


    # No longer Used
    def load_samples(self):
        print("# Loading Samples from File")
        path = self.basepath + str(self.current_bank)+'/'
        try:
            onlyfiles = [f for f in sorted(listdir(path)) if isfile(join(path, f))]
        except FileNotFoundError:
            return None
        self.sounds = []
        for file in onlyfiles:
            if file.endswith('.wav'):
                if file.startswith('.'):
                    pass
                else:
                    self.sounds.append(Soundy(path+file))
        self.sounds = self.sounds[0:self.max_bank_size]
        print(f"LOADING SOUND BANK: {self.current_bank}")
        if c.PI_FAST_LOAD:
            pass
        else:
            self.pre_process_sounds()


# SOUND PROCESSING

    def change_pitch(self,factor):
        #  self.pitch_factor * (1 - self.semitone)
        #  new factor is just (1 +/- self.semitone)
        print(f"pads currently pressed: {self.on_notes}")
        if self.on_notes: # if there are notes actively pressed
            for note in self.on_notes:
                note = note-self.button.PAD_START
                if c.THREADING_ACTIVE:
                    # Run DSP as background process
                    x = Thread(self.all_sounds[self.current_page].kits[self.current_bank].samples[note].change_pitch(factor), daemon=True)
                    x.start()
                    x = Thread(self.all_sounds[self.current_page].kits[self.current_bank].samples[note].normalize(), daemon=True)
                    x.start()
                    x = Thread(self.all_sounds[self.current_page].kits[self.current_bank].samples[note].make_loud(), daemon=True)
                    x.start()
                else:
                    self.all_sounds[self.current_page].kits[self.current_bank].samples[note].change_pitch(factor)
                    self.all_sounds[self.current_page].kits[self.current_bank].samples[note].normalize()
                    self.all_sounds[self.current_page].kits[self.current_bank].samples[note].make_loud()

        else:


            for sound in self.all_sounds[self.current_page].kits[self.current_bank].samples:

                if c.THREADING_ACTIVE:
                    # Run DSP as background process
                    x = Thread(sound.change_pitch(factor), daemon=True)
                    x.start()
                    x = Thread(sound.normalize(), daemon=True)
                    x.start()
                    x = Thread(sound.make_loud(), daemon=True)
                    x.start()
                else:
                    sound.change_pitch(factor)
                    sound.normalize()
                    sound.make_loud()

    def pre_process_sounds(self, sounds = None):
        if not sounds:
            sounds = self.sounds
        for sound in sounds:
            print(sound.path)
            sound.restrict_length(self.max_sample_length_seconds)  # Truncate Samples longer than n seconds
            sound.remove_artifacts()
            sound.normalize()
            sound.make_loud()


# SOUND PLAYING

    # MAIN INPUT MIDI SORTING LOGIC TREE

    def sort_midi(self,midi,port,time):
        print(midi)
        # if midi.channel == c.SYNTH_MIDI_CHANNEL:
        #     if midi.type == "note_on":
        #         if self.button_is_shift(midi):
        #             self.metronome_shift(midi)
        #             self.bank_shift(midi)
        #             self.loop_shift(midi)
        #         if self.button_is_playable(midi):
        #             self.add_to_loop(midi,port,time)
        #         if self.button_is_switch(midi):
        #             self.bpm_up(midi)
        #             self.bpm_down(midi)
        #             self.pitch_up(midi)
        #             self.pitch_down(midi)
        #             self.clear_loop(midi)
        #             self.record(midi)
        #             self.velocity_sensitivity(midi)
        #             self.exit_program(midi)
        #             self.switch_bank(midi)
        #             self.switch_metronome(midi)
        if midi.channel == c.MIDI_CONTROLLER_CHANNEL:
            if midi.type == "note_on":
                if self.button_is_shift(midi):
                    self.metronome_shift(midi)
                    self.page_shift(midi)
                    self.bank_shift(midi)
                    self.loop_shift(midi)
                    self.mode_shift(midi)
                    self.loop_activator_shift(midi)
                if self.button_is_playable(midi):
                    self.play_sound(note.Note(None,midi,self.current_bank,port,time,self.NON_LOOP,self.current_page))  # -2 is non-loop loop id
                    self.add_to_loop(midi,port,time)
                    #self.play_sound([midi],None,[self.current_bank],[port])
                    self.on_notes.append(midi.note)  # keep list of which pads currently pressed
                if self.button_is_switch(midi):
                    self.bpm_up(midi)
                    self.bpm_down(midi)
                    self.pitch_up(midi)
                    self.pitch_down(midi)
                    self.clear_loop(midi)
                    self.record(midi)
                    self.audio_record(midi)
                    self.velocity_sensitivity(midi)
                    self.exit_program(midi)
                    self.change_page(midi)
                    self.switch_bank(midi)
                    self.switch_metronome(midi)
                    self.activate_loop(midi)
            if midi.type == "note_off":
                if self.button_is_shift(midi):
                    self.metronome_shift(midi)
                    self.bank_shift(midi)
                    self.page_shift(midi)
                    self.loop_shift(midi)
                    self.mode_shift(midi)
                    self.loop_activator_shift(midi)
                if self.button_is_playable(midi):
                    if self.current_page > 0:
                        self.cutoff_current_sound(note.Note(None,midi,self.current_bank,port,time,self.NON_LOOP,self.current_page))
                    self.add_to_loop(midi,port,time)
                    self.on_notes.remove(midi.note)  # keep list of which pads currently pressed
            if midi.is_cc():
                self.update_mbung_vol(midi)
                self.update_col_vol(midi)
        if midi.channel == c.SYNTH_MIDI_CHANNEL:
            self.add_to_loop(midi,port,time)

            #if c.SYNTH_ONLY:


    # SHIFT FUNCTIONS - held buttons that activate selection modes

    def shift_is_active(self):
        if self.is_metronome_pressed or self.is_loop_loader_pressed or self.is_loop_saver_pressed or self.is_bank_shift_pressed\
                or self.is_mode_shift_pressed or self.is_page_shift_pressed or self.is_loop_activator_shift_pressed:
           print("Shift is active")
           return True
        else:
            return False


    def button_is_shift(self,midi):
        if midi.note in QUNEO.SHIFT_BUTTONS:
            return True
        else:
            return False

    def mode_shift(self,midi):
        if midi.note == self.button.MODE_SHIFT:
            self.is_mode_shift_pressed = not self.is_mode_shift_pressed

    def bank_shift(self,midi):
        if midi.note == self.button.BANK_SELECTOR:
            self.is_bank_shift_pressed = not self.is_bank_shift_pressed

    def page_shift(self,midi):
        if midi.note == self.button.PAGE_SELECTOR:
            self.is_page_shift_pressed = not self.is_page_shift_pressed
            print(f"page shift: {self.is_page_shift_pressed}")

    def metronome_shift(self,midi):
        if midi.note == self.button.METRONOME:
            self.is_metronome_pressed = not self.is_metronome_pressed

    def loop_shift(self,midi):
        if midi.note == self.button.LOOP_SELECTOR:
            self.is_loop_loader_pressed = not self.is_loop_loader_pressed

    def loop_activator_shift(self,midi):
        if midi.note == self.button.LOOP_ACTIVATOR_SHIFT:
            self.is_loop_activator_shift_pressed = not self.is_loop_activator_shift_pressed
            print(f"Loop activator shift ON? {self.is_loop_activator_shift_pressed}")


    # SWITCH FUNCTIONS - for changing mode or state settings

    def button_is_switch(self,midi):
        if not self.button_is_playable(midi) and not self.button_is_shift(midi) and (midi.note in QUNEO.PADS or midi.note in QUNEO.SWITCH_BUTTONS):
            return True
        else:
            return False

    def bpm_up(self,midi):
        if midi.note == self.button.BPM_UP:
            self.metronome.bpm_up()
    def bpm_down(self,midi):
        if midi.note == self.button.BPM_DOWN:
            self.metronome.bpm_down()
    def pitch_up(self,midi, for_one_sample=False):
        if midi.note == self.button.PITCH_UP:
            self.change_pitch(1 - self.semitone)
    def pitch_down(self,midi,for_one_sample=False):
        if midi.note == self.button.PITCH_DOWN:
            self.change_pitch(1 + self.semitone)
    def clear_loop(self,midi):
        if midi.note == self.button.CLEAR_LOOP:
            print("CLEARING LOOP")
            self.metronome.midi_recorder.clear_all_loops()
            self.midi_player.all_notes_off()
    def audio_record(self,midi):
        mode_num = midi.note - self.button.PAD_START
        if self.is_mode_shift_pressed and mode_num == self.button.AUDIO_RECORD_MODE_NUM:
            self.record_new_samples()
    def record(self,midi):
        if midi.note == self.button.RECORD:
            self.metronome.midi_recorder.switch_record_button()
    def velocity_sensitivity(self,midi):
        mode_num = midi.note - self.button.PAD_START
        if self.is_mode_shift_pressed and mode_num == self.button.VELOCITY_SENSITIVITY:
            self.VOL_SENS = not self.VOL_SENS
    def exit_program(self,midi):
        if midi.note == self.button.EXIT:
            print("EXITING PROGRAM")
            sys.exit()
    def switch_metronome(self,midi):
        if self.is_metronome_pressed and midi.note in self.button.PADS:
            self.metronome.switch(midi.note-self.button.PAD_START)

    def activate_loop(self, midi):
        print("ACTIVATE LOOP")
        if self.is_loop_activator_shift_pressed and midi.note in self.button.PADS:
            print("ACTIVATE LOOP")
            self.metronome.midi_recorder.activate_loop_id(midi.note-self.button.PAD_START)

    def change_page(self, midi):
        if self.is_page_shift_pressed and midi.note in self.button.PADS:
            old_page = self.current_page
            self.current_page = midi.note-self.button.PAD_START

            old_bank = self.current_bank
            #page_factor = self.current_page*self.max_page_size  # Zero indexed
            #self.current_bank = page_factor
            print(f"Changing Page to {self.current_page}, current bank is {self.current_bank}")
            try:
                self.sounds = self.all_sounds[self.current_page].kits[0]
                print(f"current page: {self.current_page}")
            except IndexError:
                self.current_bank = old_bank  # Stay on current bank
                self.current_page = old_page

    def switch_bank(self,midi):
        if self.is_bank_shift_pressed and midi.note in self.button.PADS:
            old_bank = self.current_bank
            #page_factor = self.current_page*self.max_page_size  # Zero indexed
            self.current_bank = midi.note-self.button.PAD_START #page_factor + midi.note-self.button.PAD_START
            try:
                self.sounds = self.all_sounds[self.current_page].kits[self.current_bank]
            except IndexError:
                self.current_bank = old_bank  # Stay on current bank
            # try:
            #     if c.LOAD_SAMPLES == c.ALL_SAMPLES:
            #         pass
            #     else:
            #         #  load samples as background process
            #         if c.THREADING_ACTIVE:
            #             x = Thread(target=self.load_samples, daemon=True)
            #             x.start()
            #         else:
            #             self.load_samples()
            # except FileNotFoundError:
            #     pass  # allow to be in an empty bank
            #     #self.current_bank = old_bank


    # PLAYABLE FUNCTIONS - if note plays a sound

    def button_is_playable(self,midi):
        if midi.note in QUNEO.PADS and not self.shift_is_active():
            print("button is playable")
            return True
        else:
            return False

    def add_to_loop(self,midi,port,midi_time):
        if self.metronome.midi_recorder.RECORD:
            self.metronome.midi_recorder.add_entry(midi,port,when_added=midi_time)

    # def play_sound_local(self,midi):
    #     try:
    #         i = midi.note - self.button.PAD_START
    #         if i<0:
    #             raise IndexError
    #         if self.current_bank < 4:
    #             for sound in self.sounds:
    #                 sound.stop()
    #             for sound in self.all_sounds[self.current_page].kits[self.current_bank]:
    #                 sound.stop()
    #         if self.VOL_SENS:
    #             self.sounds[i].set_volume(midi.velocity)
    #         else:
    #             self.sounds[i].set_volume(128)
    #         self.sounds[i].play(block=False)
    #     except IndexError:
    #         print("Sound not found")
    #         pass



    def play_sound(self,entry):
        if c.MIDI_CONTROLLER in entry.port:

            i = entry.midi.note - self.button.PAD_START  # get the midi note of pad
            if entry.bank < len(self.all_sounds[entry.page].kits) and i >= 0 and i < len(self.all_sounds[entry.page].kits[entry.bank].samples):  # if sound has an ID

                if self.VOL_SENS:  # set volume if volume sensitivity is turned on
                    self.all_sounds[entry.page].kits[entry.bank].samples[i].set_volume(entry.midi.velocity)
                else:
                    self.all_sounds[entry.page].kits[entry.bank].samples[i].set_volume(128)

                if entry.page == 0:
                    self.cutoff_all_sounds_in_same_bank(entry) # if any sound in same bank is playing, cut it off (hand drums)

                if entry.page > 0:
                    self.cutoff_current_sound(entry)  # if exact same sound is playing, cut it off

                if entry.midi.velocity>0:
                    self.all_sounds[entry.page].kits[entry.bank].samples[i].play(block=False)  # play sound


    # def play_sound_old(self,midis,note,banks,ports):
    #     for j,midi in enumerate(midis):
    #         if c.MIDI_CONTROLLER in ports[j]:
    #             if not note:
    #                 note = midi.note
    #             i = note - self.button.PAD_START
    #             if i>=0 and i<len(self.all_sounds[self.current_page].kits[banks[j]]):
    #                 if self.VOL_SENS:
    #                     self.all_sounds[self.current_page].kits[banks[j]][i].set_volume(midi.velocity)
    #                 else:
    #                     self.all_sounds[self.current_page].kits[banks[j]][i].set_volume(128)
    #                 if self.current_bank < 3:
    #                     for sound in self.all_sounds[self.current_page].kits[banks[j]]:
    #                         sound.stop()
    #                 else:
    #                     if midi.velocity==0 or midi.type == "note_off":
    #                         self.cutoff_sound(midi)
    #                         #self.all_sounds[self.current_page].kits[banks[j]][i].stop()
    #                         # for sound in self.all_sounds[self.current_page].kits[banks[j]]:
    #                         #     sound.stop()
    #                 if midi.velocity>0:
    #                     self.all_sounds[self.current_page].kits[banks[j]][i].play(block=False)

    # cutoff current sound
    # cutoff all sounds in same bank
    # cutoff all sounds

    def cutoff_current_sound(self,entry):
        i = entry.midi.note - self.button.PAD_START
        if entry.bank < len(self.all_sounds[entry.page].kits) and i>=0 and i<len(self.all_sounds[entry.page].kits[entry.bank].samples): # if midi note is in bank
            self.all_sounds[entry.page].kits[entry.bank].samples[i].stop() # stop sound

    def cutoff_all_sounds_in_same_bank(self,entry):
        i = entry.midi.note - self.button.PAD_START
        if entry.bank < len(self.all_sounds[entry.page].kits) and i>=0 and i<len(self.all_sounds[entry.page].kits[entry.bank].samples): # if midi note is in bank
            for sound in (self.all_sounds[entry.page].kits[entry.bank].samples):
                sound.stop() # stop sound

    def cutoff_all_sounds(self):
        for page in self.all_sounds:
            for kit in page.kits:
                for sound in kit.samples:
                    sound.stop()

    def cutoff_sound(self,entry):
        i = entry.midi.note - self.button.PAD_START
        if (entry.bank > 3) and (entry.bank < len(self.all_sounds[entry.page].kits) and i>=0 and i<len(self.all_sounds[entry.page].kits[entry.bank].samples)):
            #self.sounds[i].stop()
            self.all_sounds[entry.page].kits[entry.bank].samples[i].stop()


    # CHANGE CONTROL FUNCTIONS

    def update_mbung_vol(self,midi):
        if midi.control == self.button.MBUNG_VOL_CONTROL:  # mbungmbung volume
            drum = 0
            self.metronome.update_volume(drum,midi.value)

    def update_col_vol(self,midi):
        if midi.control == self.button.COL_VOL_CONTROL:  # mbungmbung volume
            drum = 1
            self.metronome.update_volume(drum,midi.value)


    # Record Sound
    def record_new_samples(self):
        print("RECORDING NEW SAMPLES")
        # create recording
        r = AudioRecorder(self.sample_recording_length_in_seconds)
        r.start_record()
        r.stop_record()

        # generate wav file
        r.create_wav()

        # slice wav and export it to current_bank
        Slicer(r.WAVE_OUTPUT_FILENAME,[0,r.RECORD_SECONDS],self.current_bank)

        # Reload the samples in current bank
        self.reload_bank(self.current_bank)


MidiControl()
