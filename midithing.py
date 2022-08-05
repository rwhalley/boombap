#!/usr/bin/python

import time
import os
import glob
from os import listdir
from os.path import isfile, join, exists
import sys
from pathlib import Path
from threading import Thread
import pickle as p
from dataclasses import dataclass
from datetime import datetime as dt

import mido
import numpy as np

from soundy_pygame import Soundy
from metronome import Metronome
import QUNEO
import REFACE
from midiout import MIDIPlayer
from midi_recorder import MIDIRecorder
from recorder import AudioRecorder
from slicer import Slicer
import CONFIG as c
import note_class
from page  import Kit, Page


class MidiControl:

    def __init__(self):
        #os.nice(-20)
        self.basepath = c.USB  # # # str(Path(__file__).parent / 'samples/')+'/'
        self.program_path = c.PROGRAM_PATH
        self.save_path = self.program_path+'/pickle/the_sounds'
        self.current_bank = 0
        self.current_page = 0
        self.max_sample_length_seconds = 3
        self.max_page_size = 16
        self.max_bank_size = 16
        self.button = QUNEO
        self.VOL_SENS = False
        self.METRONOME_MUTE = False
        self.port_name = None
        self.ports = []
        self.last_note = 1101001
        self.NON_LOOP = -2
        self.active_controllers = {10}
        self.time_since_last_cc = time.time()
        self.global_vol = 128

        # -- Sound Data ---
        self.all_sounds = [self.get_empty_page()] * 16
        self.all_sound_data = None

        # --- Shift Button States ---
        self.is_metronome_pressed = False
        self.track_save_shift_pressed = False
        self.track_load_shift_pressed = False
        self.is_bank_shift_pressed = False
        self.is_mode_shift_pressed = False
        self.is_page_shift_pressed = False
        self.is_volume_shift_pressed = False
        self.is_loop_activator_shift_pressed = False
        self.is_reverb_shift_pressed = False

        # --- Switch Button States ---
        self.is_keyboard_active = False

        self.sample_id = None

        self.on_notes = list()#set()
        self.cut_group = list()

        self.devices = [] # QUNEO, Reface CP
        self.messages = []
        self.threads = []
        self.control_msgs = []
        self.devices = list(set(mido.get_input_names()))
        print(self.devices)

        # LOAD SAMPLES - Try Fast Load

        if c.DEBUG:
            pass
        else:
            path = self.program_path+"/pickle/"
            if(not os.path.exists(path)):
                os.makedirs(path)
            onlyfiles = [f for f in sorted(listdir(path)) if isfile(join(path, f))]
            if len(onlyfiles)>0 and not c.SIMPLE_MODE:#exists(self.save_path):
                self.load_all_sound_data()
            else:
                if c.SIMPLE_MODE:
                    self.load_all_samples()
                    for page in self.all_sounds:
                        if page:
                            for kit in page.kits:
                                self.pre_process_sounds(sounds = kit.samples)

                self.save_all_sound_data()

        # AUDIO RECORDER
        self.sample_recording_length_in_seconds = 5

        # START METRONOME
        self.metronome_path = self.program_path + 'metronome/metronome.wav'
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


        # Setup LED control for QUNEO
        self.LED_out = None
        print("INITIALIZING LED OUT")
        print(c.MIDI_CONTROLLER in c.POSSIBLE_MIDI_CONTROLLERS)
        #     print("Creating LED OUT")
        self.LED_out = MIDIPlayer(None,c.MIDI_CONTROLLER,light=True)

        for i in range(0,60):
            self.LED_out.play_note(note_class.Note(0,mido.Message('note_on', note=i),0,c.MIDI_CONTROLLER,time.time(), -2,0), light=True)
            time.sleep(0.005)

        for i in range(0,60):
            self.LED_out.play_note(note_class.Note(0,mido.Message('note_off', note=i),0,c.MIDI_CONTROLLER,time.time(), -2,0), light=True)
            time.sleep(0.005)

        self.LED_out.play_note(note_class.Note(0,mido.Message('note_on', note=self.button.ON_LED),0,c.MIDI_CONTROLLER,time.time(), -2,0), light=True)




        self.metronome.tada.play(block=False)

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
                                if note.sample_id or note.sample_id == 0:
                                    self.play_sound(note)

                                else:
                                    self.midi_player.play_note(note)
                            if note.port in c.MIDI_CONTROLLER:
                                if note.midi.type == "note_on":
                                    self.play_sound(note)
                                if note.midi.type == "note_off":
                                    if note.page > 0 and not ([note.page,note.bank, note.midi.note-self.button.PAD_START]) in self.cut_group:

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
        else:
            if midi.control in self.active_controllers:
                print(midi.value)
                self.set_global_volume(midi)

        # elif midi.type == 'control_change':
        #    self.control_msgs.append(midi)
        # if midi.type == 'note_off' and len(self.control_msgs) >1:
        #     msg = self.control_msgs[-2]
        #     self.control_msgs = []
        #     if msg.channel == c.MIDI_CONTROLLER_CHANNEL:
        #         self.sort_midi(msg,c.MIDI_CONTROLLER,now)


# SAMPLE LOADING

    def get_empty_page(self, name="", path=""):
        return Page(name,path,[Kit(None,None,[Soundy(no_init=True)]*16,[128]*16)]*16)

    def get_empty_kit(self, name=None, path=None):
        return Kit(name,path,[Soundy(no_init=True)]*16,[128]*16)

    def reload_page(self,page_num):
        newpage = self.get_empty_page()
        self.all_sounds[page_num] = newpage
        page = c.RECORDED_SAMPLES_FOLDER

        kits_names = self.get_all_kit_dirs(self.basepath + '/'+page+'/')

        kits = [self.get_empty_kit()] * 16
        for i, kit_name in enumerate(kits_names[page_num]):
            kit = self.get_empty_kit(name = kit_name, path =self.basepath+'/'+page+'/'+kit_name+'/')
            samples = [f for f in sorted(listdir(kit.path)) if isfile(join(kit.path, f))]
            for j, file in enumerate(samples):
                if file.endswith('.wav'):
                    if file.startswith('.'):
                        pass
                    else:
                        kit.samples[j] = (Soundy(kit.path+file))

            kits[i] = (kit)

        self.all_sounds[page_num] = (Page(page,self.basepath+'/'+page+'/',kits))
        self.save_page(page_num)


    def reload_kit(self,kit_num,page_num):
        path = self.basepath+'/'+c.RECORDED_SAMPLES_FOLDER+'/'+str(kit_num)+'/'
        if not exists(path):
            os.makedirs(self.basepath+'/'+c.RECORDED_SAMPLES_FOLDER+'/'+str(kit_num)+'/')
        kit = self.get_empty_kit(name=str(kit_num),path = path)
        samples = [f for f in sorted(listdir(kit.path)) if isfile(join(kit.path, f))]
        print("RELOAD KIT")
        print(f"PAGE NUM {page_num}")
        print(f"KIT NUM {kit_num}")
        for i, file in enumerate(samples):

            print(file)
            if file.endswith('.wav') and i<c.NUM_PADS:
                if file.startswith('.'):
                    pass
                else:
                    #print(f"filename: {file}")
                    kit.samples[i] = (Soundy(kit.path+file))

        if self.all_sounds[page_num].kits:
            print("MAKING KIT")
            self.all_sounds[page_num].kits[kit_num] = (kit)
        else:
            self.reload_page(page_num)

        self.pre_process_sounds(sounds = self.all_sounds[self.current_page].kits[self.current_bank].samples)

        self.save_page(page_num)
        self.metronome.tada.play(block=False)



    def save_page(self,page_num):
        i = page_num
        if exists(self.save_path+str(i)+ ".pkl"):
            print(f"Removed Old Pickle File: {self.save_path+str(i) +'.pkl'} ")
            os.remove(self.save_path+str(i) +".pkl")
        page = self.all_sounds[page_num]
        newpage = self.get_empty_page()

        for j, kit in enumerate(page.kits):
            #print(f"length: {len(page.kits)}")
            newkit = self.get_empty_kit()
            if kit:
                for k,sound in enumerate(kit.samples):
                    if sound and k<16:
                        #print(f"k: {k}")
                        #print(sound.path)
                        newkit.samples[k]= sound.get_original_sound_array()
                        newkit.volumes[k] = sound.vol
                #print(f"kit len:{len(kit.samples)}")
                #print(f"j {j}")
                newpage.kits[j] = newkit
        self.all_pages[i] = (newpage)
        print(f"SAVING Page {i+1} of {len(self.all_sounds)}")

        p.dump(newpage, open(self.save_path+str(i)+".pkl",'wb'))




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
        self.pre_process_sounds(sounds = self.all_sounds[self.current_page].kits[bank_num].samples)

    def load_all_sound_data(self):
        print("# Loading Sound Data from Pickle")
        path = self.program_path+"pickle/"
        onlyfiles = [f for f in sorted(listdir(path)) if isfile(join(path, f))]
        self.all_pages = [self.get_empty_page()] * 16
        self.all_sounds = [self.get_empty_page()] * 16


        for i,file in enumerate(onlyfiles):
            self.all_pages[i] = p.load(open(self.save_path+str(i)+".pkl",'rb'))

        for i, page in enumerate(self.all_pages):
            #print(f"page: {page}")
            if page:
                newpage = self.get_empty_page()
                for j, kit in enumerate(page.kits):
                    newkit = self.get_empty_kit()
                    if kit:
                        #print(kit.samples)
                        newkit.path = kit.path
                        for k, sound_arr in enumerate(kit.samples):
                            #print(f"ksoundarr: {k}")
                            if k <16:
                                try:
                                    newkit.samples[k] = Soundy(fast_load=True, arr=sound_arr)
                                    newkit.samples[k].set_volume(kit.volumes[k])
                                except ValueError:
                                    pass
                                    #print(f"soundarr: {sound_arr}")
                        newpage.kits[j] = newkit
                self.all_sounds[i] = newpage
        # for page in self.all_sounds:
        #     if page:
        #         for kit in page.kits:
        #             if kit:
        #                 self.pre_process_sounds(sounds = kit.samples)
        #self.load_volume_levels()
        print("# Sound Data Loaded from Pickle")


    def save_all_sound_data(self):
        print("# Saving Sound Data to Pickle")
        self.all_pages = [self.get_empty_page()] * 16
        for i, page in enumerate(self.all_sounds):
            newpage = self.get_empty_page()
            if page:
                for j, kit in enumerate(page.kits):

                    newkit = self.get_empty_kit()

                    if kit:
                        newkit.path = kit.path
                        for k,sound in enumerate(kit.samples):
                            if sound:
                                #print(sound.path)
                                newkit.samples[k]= sound.get_original_sound_array()
                                newkit.volumes[k] = sound.vol
                        newpage.kits[j] = newkit
                self.all_pages[i] = (newpage)
                print(f"SAVING Page {i+1} of {len(self.all_sounds)}")
                if exists(self.save_path+str(i)+ ".pkl"):
                    print(f"Removed Old Pickle File: {self.save_path+str(i) +'.pkl'} ")
                    os.remove(self.save_path+str(i) +".pkl")
                p.dump(newpage, open(self.save_path+str(i)+".pkl",'wb'))
        self.all_pages = [self.get_empty_page()] * 16
        print("# Sound Data Saved to Pickle")

    def reload_all_sound_data(self):
        print("# Clearing all sound data")
        self.all_sounds = [self.get_empty_page()] * 16
        self.all_pages = [self.get_empty_page()] * 16
        self.all_sound_data = []
        print("# Reloading all sound data")
        self.load_all_samples()
        self.save_all_sound_data()


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
        self.all_sounds = [self.get_empty_page()] * 16
        for i, page in enumerate(pages):
            kits = [self.get_empty_kit()] * 16
            for j, kit_name in enumerate(kits_names[i]):
                kit = self.get_empty_kit(name=kit_name, path = self.basepath+'/'+page+'/'+kit_name+'/')
                samples = [f for f in sorted(listdir(kit.path)) if isfile(join(kit.path, f))]
                sub = 0
                for k, file in enumerate(samples):
                    if file.endswith('.wav'):
                        if file.startswith('.'):
                            sub += 1
                            pass
                        else:
                            if k<(16+sub):
                                #print(file)

                                kit.samples[k-sub] = (Soundy(kit.path+file))

                    else:
                        sub+=1

                kits[j] = (kit)

            self.all_sounds[i] = (Page(page,self.basepath+'/'+page+'/',kits))

            print(f"Loading page '{page}' - {i+1} of {len(pages)}")
        #print(self.all_sounds)
        print("--- Raw Sounds Loaded into Memory ---")
            #print(self.all_sounds)


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

    def apply_reverb(self):
        if self.is_reverb_shift_pressed:
            if self.on_notes:
                for note in self.on_notes:
                    note = note-self.button.PAD_START
                    self.all_sounds[self.current_page].kits[self.current_bank].samples[note].apply_reverb()




    def change_pitch(self,factor):
        #  self.pitch_factor * (1 - self.semitone)
        #  new factor is just (1 +/- self.semitone)
        print(f"pads currently pressed: {self.on_notes}")
        if self.on_notes: # if there are notes actively pressed
            for note in self.on_notes:
                note = note-self.button.PAD_START
                if self.all_sounds[self.current_page].kits[self.current_bank].samples[note].pgsound:
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
                if sound.pgsound:
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
        num_sounds = len(sounds)
        for i, sound in enumerate(sounds):
            if sound.pgsound:
                #print(sound.path)
                print(f"Processing Sound {i+1} of {len(sounds)}")
                sound.restrict_length(self.max_sample_length_seconds)  # Truncate Samples longer than n seconds
                sound.remove_artifacts()
                sound.normalize()
                sound.make_loud()
        print(f"Sound Processing Complete")


# SOUND PLAYING

    # MAIN INPUT MIDI SORTING LOGIC TREE

    def sort_midi(self,midi,port,time):
        print(midi)
        # if midi.channel == c.SYNTH_MIDI_CHANNEL:
        #     if midi.type == "note_on":
        #         if self.button_is_shift(midi):
        #             self.metronome_shift(midi)
        #             self.bank_shift(midi)
        #             self.track_load_shift(midi)
        #             self.track_save_shift(midi)

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
            if midi.type == "note_on" :
                if self.button_is_shift(midi):
                    self.metronome_shift(midi)
                    self.page_shift(midi)
                    self.bank_shift(midi)
                    self.track_load_shift(midi)
                    self.track_save_shift(midi)
                    self.mode_shift(midi)
                    self.loop_activator_shift(midi)
                    self.volume_shift(midi)
                    self.reverb_shift(midi)
                if self.button_is_playable(midi):
                    self.play_sound(note_class.Note(None, midi, self.current_bank, port, time, self.NON_LOOP, self.current_page))  # -2 is non-loop loop id
                    self.add_to_loop(midi,port,time)
                    #self.play_sound([midi],None,[self.current_bank],[port])
                    self.on_notes.append(midi.note)  # keep list of which pads currently pressed
                    self.make_keyboard(midi) # Create Keyboard

                if self.button_is_switch(midi):

                    self.bpm_up(midi)
                    self.bpm_down(midi)
                    self.pitch_up(midi)
                    self.pitch_down(midi)
                    self.clear_loop(midi)
                    self.record(midi)
                    self.audio_record(midi)
                    self.switch_loop_length(midi)
                    self.mute_metronome(midi)

                    self.save_state(midi)

                    self.velocity_sensitivity(midi)
                    self.exit_program(midi)

                    self.change_page(midi)
                    self.switch_bank(midi)
                    self.switch_metronome(midi)
                    self.activate_loop(midi)
                    self.save_track(midi)
                    self.load_track(midi)
                    self.reload_samples(midi)
                    self.keyboard(midi)




            if midi.type == "note_off":
                if self.button_is_shift(midi):
                    self.metronome_shift(midi)
                    self.bank_shift(midi)
                    self.page_shift(midi)
                    self.track_save_shift(midi)
                    self.track_load_shift(midi)
                    self.mode_shift(midi)
                    self.loop_activator_shift(midi)
                    self.volume_shift(midi)
                    self.reverb_shift(midi)
                if self.button_is_playable(midi):
                    if self.current_page > 0 and not ([self.current_page,self.current_bank,(midi.note-self.button.PAD_START)] in self.cut_group):
                        self.cutoff_current_sound(note_class.Note(None, midi, self.current_bank, port, time, self.NON_LOOP, self.current_page))
                    self.add_to_loop(midi,port,time)
                    try:
                        print(self.on_notes)
                        self.on_notes.remove(midi.note) # keep list of which pads currently pressed
                    except KeyError:
                        self.on_notes = list() #set()
                    except ValueError:
                        self.on_notes = list()
                if self.button_is_switch(midi) and self.LED_out:
                    self.record_LED(midi)
                    self.keyboard_mode_LED(midi)
            if midi.is_cc():
                self.update_mbung_vol(midi)
                self.update_col_vol(midi)
        if midi.channel == c.SYNTH_MIDI_CHANNEL:
            if self.is_keyboard_active:
                if midi.velocity > 0:
                    self.play_keyboard(midi)
                if midi.velocity == 0:
                    self.cut_keyboard(midi)
                self.add_to_loop(midi,port,time, sample_id=self.sample_id)
            else:
                self.add_to_loop(midi,port,time)


            #if c.SYNTH_ONLY:


    # SHIFT FUNCTIONS - held buttons that activate selection modes

    def shift_is_active(self):
        if self.is_metronome_pressed or self.track_save_shift_pressed or self.track_load_shift_pressed or self.is_bank_shift_pressed\
                or self.is_mode_shift_pressed or self.is_page_shift_pressed or self.is_loop_activator_shift_pressed or self.is_volume_shift_pressed\
                or self.is_reverb_shift_pressed:
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
            print(f"Kit shift: {self.is_bank_shift_pressed}")

            # SWAP SAMPLES FUNCTION
            if len(self.on_notes) == 2 and  self.is_bank_shift_pressed:
                l = self.on_notes
                one = l[0]-self.button.PAD_START
                two = l[1]-self.button.PAD_START

                temp = self.all_sounds[self.current_page].kits[self.current_bank].samples[one]
                self.all_sounds[self.current_page].kits[self.current_bank].samples[one] = self.all_sounds[self.current_page].kits[self.current_bank].samples[two]
                self.all_sounds[self.current_page].kits[self.current_bank].samples[two] = temp
                print(f"SWAPPING SOUNDS: {one} and {two}")


    def page_shift(self,midi):
        if midi.note == self.button.PAGE_SELECTOR:
            self.is_page_shift_pressed = not self.is_page_shift_pressed
            print(f"Page shift: {self.is_page_shift_pressed}")


            if len(self.on_notes) == 2 and self.is_page_shift_pressed:
                l = self.on_notes
                one = l[0] - self.button.PAD_START
                two = l[1] - self.button.PAD_START

                # merge second sample onto first sample
                print("MERGING SAMPLES")
                new = np.concatenate((self.all_sounds[self.current_page].kits[self.current_bank].samples[one].get_original_sound_array(),self.all_sounds[self.current_page].kits[self.current_bank].samples[two].get_original_sound_array()),axis=0)
                self.all_sounds[self.current_page].kits[self.current_bank].samples[one].make_sound(new)

                # keep second sample for now


    def metronome_shift(self,midi):
        if midi.note == self.button.METRONOME:
            self.is_metronome_pressed = not self.is_metronome_pressed

    def track_save_shift(self,midi):
        if midi.note == self.button.TRACK_SAVE_SHIFT:
            self.track_save_shift_pressed = not self.track_save_shift_pressed

            if self.track_save_shift_pressed:

                print(f"cut group members: {self.cut_group}")
                for note in  self.on_notes:
                    if [self.current_page,self.current_bank,note - self.button.PAD_START] in self.cut_group:
                        print(f"removing from cut group: {note}")
                        self.cut_group.remove([self.current_page,self.current_bank,note - self.button.PAD_START])
                        self.all_sounds[self.current_page].kits[self.current_bank].samples[note - self.button.PAD_START].cut_group = None

                    else:
                        print(f"adding to cut group: {note}")
                        self.cut_group.append([self.current_page,self.current_bank,note - self.button.PAD_START])
                        self.all_sounds[self.current_page].kits[self.current_bank].samples[note - self.button.PAD_START].cut_group = 1

    def track_load_shift(self,midi):
        if midi.note == self.button.TRACK_LOAD_SHIFT:
            self.track_load_shift_pressed = not self.track_load_shift_pressed


            # # COPY SAMPLE TO KIT ROUTINE
            # if self.track_load_shift_pressed:
            #
            #     for note in  self.on_notes:



    def loop_activator_shift(self,midi):
        if midi.note == self.button.LOOP_ACTIVATOR_SHIFT:
            self.is_loop_activator_shift_pressed = not self.is_loop_activator_shift_pressed
            print(f"Loop activator shift ON? {self.is_loop_activator_shift_pressed}")

    def volume_shift(self,midi):
        if midi.note == self.button.VOLUME_SHIFT:
            self.is_volume_shift_pressed = not self.is_volume_shift_pressed
            print(f"Volume Shift: {self.is_volume_shift_pressed}")

    def reverb_shift(self,midi):
        if midi.note == self.button.REVERB:
            self.is_reverb_shift_pressed = not self.is_reverb_shift_pressed
            print(f"Reverb Shift: {self.is_reverb_shift_pressed}")
        self.apply_reverb()

    # SWITCH FUNCTIONS - for changing mode or state settings

    def button_is_switch(self,midi):

        if not self.button_is_playable(midi) \
                and not self.button_is_shift(midi) \
                and (midi.note in QUNEO.PADS or midi.note in QUNEO.SWITCH_BUTTONS):
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
            self.change_pitch(1 - c.SEMITONE)
    def pitch_down(self,midi,for_one_sample=False):
        if midi.note == self.button.PITCH_DOWN:
            self.change_pitch(1 + c.SEMITONE)
    def load_volume_levels(self):
        for page in self.all_sounds:
            for kit in page.kits:
                for sound in kit.samples:
                    try:
                        sound.set_volume(sound.vol)
                    except AttributeError:
                        pass

    def set_global_volume(self,midi): # vol is 0-127
        if midi.value<25:
            midi.value = 25
        #print(f"midi:{midi.value}")
        now = time.time()


        if self.on_notes: # if there are notes actively pressed, sample level volume adjustment
            for note in self.on_notes:
                i = note-self.button.PAD_START
                self.all_sounds[self.current_page].kits[self.current_bank].samples[i].vol = midi.value
                self.all_sounds[self.current_page].kits[self.current_bank].samples[i].set_volume(midi.value)
        elif self.is_mode_shift_pressed:  # global volume level adjustment
            #print(f"time: {(now-self.time_since_last_cc)}")
            if (now-self.time_since_last_cc) >0.5:
                factor  = (midi.value/self.global_vol)


                for page in self.all_sounds:
                    for kit in page.kits:
                        for sound in kit.samples:
                            try:
                                sound.vol = (sound.vol)*(factor)
                                sound.set_volume(sound.vol)
                            except AttributeError:
                                pass
                                #print("empty entry")
                self.global_vol = midi.value
        elif self.is_metronome_pressed: # adjust levels of metronome/accompaniment
            if (now-self.time_since_last_cc) >0.5:
                factor  = (midi.value/self.global_vol)

                self.metronome.sound.set_volume(self.metronome.sound.vol*factor)
                self.metronome.update_volume(self.metronome.sound.vol*factor) # same as metronome for now



        else:  # kit level vol adjustment

            if (now-self.time_since_last_cc) >0.5:
                factor  = (midi.value/self.global_vol)

                for sound in self.all_sounds[self.current_page].kits[self.current_bank].samples:
                    try:
                        sound.vol = (sound.vol)*(factor)
                        sound.set_volume(sound.vol)
                    except AttributeError:
                        pass
                        #print("empty entry")
                self.global_vol = midi.value

        self.time_since_last_cc = now



    def clear_loop(self,midi):

        if midi.note == self.button.CLEAR_LOOP:
            if self.is_bank_shift_pressed:
                self.delete_samples(midi)
            else:
                if self.metronome.is_on:
                    print("CLEARING LOOP")

                    self.metronome.midi_recorder.clear_all_loops()
                    self.midi_player.all_notes_off()
                else:
                    self.delete_sample()
    def audio_record(self,midi):
        mode_num = midi.note - self.button.PAD_START
        if self.is_mode_shift_pressed:
            if mode_num == self.button.AUDIO_RECORD_MODE_NUM:
                print("LEAST SLICE")
                self.record_new_samples(slice_sharpness = 0.3)
            if mode_num == self.button.AUDIO_RECORD_MODE_NUM_SHARP:
                print("MOST SLICE")
                self.record_new_samples(slice_sharpness = 0.1)
            if mode_num == self.button.AUDIO_RECORD_NO_SLICE:
                print("NO SLICE")
                self.record_new_samples(slice_sharpness = None)






    def delete_sample(self, archive = True):
        archive_folder = c.ARCHIVE + str(dt.now().strftime("%y%m%d%H%M%S"))+"/"
        current_folder = self.all_sounds[self.current_page].kits[self.current_bank].path
        listdir = os.listdir(current_folder)

        if not os.path.exists(archive_folder):
            os.makedirs(archive_folder)

        for note in self.on_notes:
            note = note - self.button.PAD_START


            # archive the file
            if c.RECORDED_SAMPLES_FOLDER in current_folder:
                if archive:
                    for i,f in enumerate(listdir):
                        if i == note:
                            os.rename(current_folder + f, archive_folder + f) # move file

            # reset the sound
            self.all_sounds[self.current_page].kits[self.current_bank].samples[note] = Soundy(no_init=True)

            print(f"DELETING SAMPLE: {note}")

            #  resave the page
            self.save_page(self.current_page)



    def delete_samples(self,midi, archive=True):
        archive_folder = c.ARCHIVE + str(dt.now().strftime("%y%m%d%H%M%S"))+"/"
        if not os.path.exists(archive_folder):
            os.makedirs(archive_folder)
        current_folder = self.all_sounds[self.current_page].kits[self.current_bank].path
        if '10' in current_folder:
            if archive:
                for f in os.listdir(current_folder):
                    os.rename(current_folder + f, archive_folder + f)
        self.all_sounds[self.current_page].kits[self.current_bank] = self.get_empty_kit(path = current_folder)
        print(f"CLEARED KIT: {current_folder}")
        self.save_page(self.current_page)


            # else:  # delete
            #     files = glob.glob(folder)
            #     print(files)
            #     for f in files:
            #         os.remove(f)
            #     pass

    def keyboard(self,midi):
        if midi.note == self.button.KEYBOARD:
            self.is_keyboard_active = not self.is_keyboard_active
            print(f"KEYBOARD MODE: {self.is_keyboard_active}")


    def make_keyboard(self, midi):
        if self.is_keyboard_active:

            self.sample_id = midi.note - self.button.PAD_START
            #print(self.sample_id)

            if self.all_sounds[self.current_page].kits[self.current_bank].samples[self.sample_id].pgsound:
                print("--- MAKING KEYBOARD ---")

                self.all_sounds[self.current_page].kits[self.current_bank].samples[self.sample_id].make_keyboard(start_semitone=12,num_keys=25)  # play sound

    def play_keyboard(self,midi):

        note = midi.note - REFACE.C0_OFFSET
        #print(f"note {note}")
        if self.is_keyboard_active:
            try:
                self.all_sounds[self.current_page].kits[self.current_bank].samples[self.sample_id].play(block=False, key=note)
            except IndexError:
                pass

    def cut_keyboard(self,midi):
        note = midi.note - REFACE.C0_OFFSET
        if self.is_keyboard_active:
            try:
                self.all_sounds[self.current_page].kits[self.current_bank].samples[self.sample_id].stop(key=note)
            except IndexError:
                pass

    def record(self,midi):
        if midi.note == self.button.RECORD:
            self.metronome.midi_recorder.switch_record_button()
    def record_LED(self,midi):
        if midi.note == self.button.RECORD:
            if self.metronome.midi_recorder.RECORD:
                self.LED_out.play_note(note_class.Note(0, mido.Message('note_on', note=self.button.RECORD_LED), 0, c.MIDI_CONTROLLER, time.time(), -2, 0), light=True)
            else:
                self.LED_out.play_note(note_class.Note(0, mido.Message('note_off', note=self.button.RECORD_LED), 0, c.MIDI_CONTROLLER, time.time(), -2, 0), light=True)

    def keyboard_mode_LED(self,midi):
        if midi.note == self.button.KEYBOARD:
            if self.is_keyboard_active:
                self.LED_out.play_note(note_class.Note(0, mido.Message('note_on', note=self.button.KEYBOARD_LED), 0, c.MIDI_CONTROLLER, time.time(), -2, 0), light=True)
            else:
                self.LED_out.play_note(note_class.Note(0, mido.Message('note_off', note=self.button.KEYBOARD_LED), 0, c.MIDI_CONTROLLER, time.time(), -2, 0), light=True)

    def metronome_LED_on(self):
        self.LED_out.play_note(note_class.Note(0, mido.Message('note_on', note=self.button.METRONOME_LED), 0, c.MIDI_CONTROLLER, time.time(), -2, 0), light=True)

    def metronome_LED_off(self):
        self.LED_out.play_note(note_class.Note(0, mido.Message('note_off', note=self.button.METRONOME_LED), 0, c.MIDI_CONTROLLER, time.time(), -2, 0), light=True)




    def load_track(self,midi):
        id = midi.note - self.button.PAD_START
        if self.track_load_shift_pressed:
            self.metronome.midi_recorder.load_track(id)
    def save_track(self,midi):
        id = midi.note - self.button.PAD_START
        if self.track_save_shift_pressed:
            self.metronome.midi_recorder.save_track(id)


    def switch_loop_length(self,midi):
        mode_num = midi.note - self.button.PAD_START
        if self.is_mode_shift_pressed and mode_num == self.button.SWITCH_LOOP_LENGTH:
            if self.metronome.bars_per_loop == 4:
                self.metronome.bars_per_loop = 8
            elif self.metronome.bars_per_loop == 8:
                self.metronome.bars_per_loop = 4
    def velocity_sensitivity(self,midi):
        mode_num = midi.note - self.button.PAD_START
        if self.is_mode_shift_pressed and mode_num == self.button.VELOCITY_SENSITIVITY:
            self.VOL_SENS = not self.VOL_SENS
    def reload_samples(self,midi):
        mode_num = midi.note - self.button.PAD_START
        if self.is_mode_shift_pressed and mode_num == self.button.RELOAD_ALL_SOUND_DATA:
            self.reload_all_sound_data()
    def mute_metronome(self,midi):
        mode_num = midi.note - self.button.PAD_START
        if self.is_mode_shift_pressed and mode_num == self.button.MUTE_METRONOME:
            self.METRONOME_MUTE = not self.METRONOME_MUTE
    def save_state(self,midi):
        mode_num = midi.note - self.button.PAD_START
        if self.is_mode_shift_pressed and mode_num == self.button.SAVE_STATE:
            print("SAVING...")
            self.save_all_sound_data()
            print("SAVED")
    def exit_program(self,midi):
        if midi.note == self.button.EXIT:
            print("EXITING PROGRAM")
            if c.MIDI_CONTROLLER == 'QUNEO':
                for i in range(0,60):
                    self.LED_out.play_note(note_class.Note(0,mido.Message('note_off', note=i),0,c.MIDI_CONTROLLER,time.time(), -2,0), light=True)

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
                if self.all_sounds[self.current_page]:
                    self.sounds = self.all_sounds[self.current_page].kits[0]
                    print(f"current page: {self.current_page}")
            except IndexError:
                self.current_bank = old_bank  # Stay on current bank
                self.current_page = old_page

    def switch_bank(self,midi):
        if self.is_bank_shift_pressed and midi.note in self.button.PADS:
            old_bank = self.current_bank
            #page_factor = self.current_page*self.max_page_size  # Zero indexed
            #print(midi.note)
            self.current_bank = midi.note-self.button.PAD_START #page_factor + midi.note-self.button.PAD_START
            #print(self.current_bank)
            try:
                self.sounds = self.all_sounds[self.current_page].kits[self.current_bank]
                print(f"Changing kit to {self.current_bank}")
            except IndexError:
                self.current_bank = old_bank  # Stay on current bank
                print(f"IndexError: kit ID {self.current_bank} not found")


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
            #print("button is playable")
            return True
        else:
            return False

    def add_to_loop(self,midi,port,midi_time, sample_id = None):
        if self.metronome.midi_recorder.RECORD:
            self.metronome.midi_recorder.add_entry(midi,port,when_added=midi_time, sample_id=sample_id)

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
            if self.check_entry(entry):

                if self.VOL_SENS:  # set volume if volume sensitivity is turned on
                    self.all_sounds[entry.page].kits[entry.bank].samples[i].set_volume(entry.midi.velocity)
                else:
                    pass # set max volume for all samples when VOL_SENS turned off not every time...
                    # self.all_sounds[entry.page].kits[entry.bank].samples[i].set_volume(128)

                if [self.current_page,self.current_bank,i] in self.cut_group:
                    for j in self.cut_group:
                        self.cutoff_current_sound(None,i=j)


                if entry.page == 0:
                    self.cutoff_all_sounds_in_same_bank(entry) # if any sound in same bank is playing, cut it off (hand drums)

                if entry.page > 0:
                    self.cutoff_current_sound(entry)  # if exact same sound is playing, cut it off

                if entry.midi.velocity>0:
                    if self.all_sounds[entry.page].kits[entry.bank].samples[i].pgsound:
                        self.all_sounds[entry.page].kits[entry.bank].samples[i].play(block=False)  # play sound
        if c.SYNTH in entry.port:

            self.all_sounds[entry.page].kits[entry.bank].samples[entry.sample_id].stop(key=(entry.midi.note- REFACE.C0_OFFSET))

            if entry.midi.velocity>0:
                self.all_sounds[entry.page].kits[entry.bank].samples[entry.sample_id].play(block=False, key=(entry.midi.note- REFACE.C0_OFFSET))


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
    def check_entry(self,entry):
        i = entry.midi.note - self.button.PAD_START
        try:
            if self.all_sounds[entry.page] and self.all_sounds[entry.page].kits[entry.bank] and self.all_sounds[entry.page].kits[entry.bank].samples and self.all_sounds[entry.page].kits[entry.bank].samples[i] and entry.bank < len(self.all_sounds[entry.page].kits) and i >= 0 and i < len(self.all_sounds[entry.page].kits[entry.bank].samples):  # if sound has an ID
                return True
            else:
                return False
        except IndexError:
            return False

    def cutoff_current_sound(self,entry, i = None):
        if not i:
            i = entry.midi.note - self.button.PAD_START
            if self.check_entry(entry):
                self.all_sounds[entry.page].kits[entry.bank].samples[i].stop() # stop sound
        else:
            self.all_sounds[i[0]].kits[i[1]].samples[i[2]].stop() # stop sound

    def cutoff_all_sounds_in_same_bank(self,entry):
        i = entry.midi.note - self.button.PAD_START
        if self.check_entry(entry):
            for sound in (self.all_sounds[entry.page].kits[entry.bank].samples):
                if sound:
                    sound.stop() # stop sound

    def cutoff_all_sounds(self):
        for page in self.all_sounds:
            for kit in page.kits:
                for sound in kit.samples:
                    if sound:
                        sound.stop()

    def cutoff_sound(self,entry):
         i = entry.midi.note - self.button.PAD_START
         if (entry.bank > 3) and self.check_entry(entry):
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
    def record_new_samples(self, slice_sharpness = 0.3):
        print("RECORDING NEW SAMPLES")
        # create recording
        r = AudioRecorder(self.sample_recording_length_in_seconds,controller=self)
        r.start_record()
        r.stop_record()

        # generate wav file
        r.create_wav()

        # slice wav and export it to current_bank

        Slicer(r.WAVE_OUTPUT_FILENAME,[0,r.RECORD_SECONDS],self.current_bank, slice_sharpness = slice_sharpness)

        r.delete_wav()

        # Reload the samples in current bank
        self.reload_kit(self.current_bank,self.current_page)


MidiControl()
