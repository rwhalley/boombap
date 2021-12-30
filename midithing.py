#!/usr/bin/python

import time
from os import listdir
from os.path import isfile, join
import sys
from pathlib import Path
from threading import Thread

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


class MidiControl:

    def __init__(self):

        self.basepath = str(Path(__file__).parent / 'samples/')+'/'
        self.current_bank = 0
        self.max_sample_length_seconds = 3
        self.max_bank_size = 16
        self.button = QUNEO
        self.VOL_SENS = False
        self.port_name = None
        self.ports = []
        self.pitch_factor = 1.0
        self.semitone = .059463094359
        self.last_note = 1101001

        # --- Shift Button States ---
        self.is_metronome_pressed = False
        self.is_loop_loader_pressed = False
        self.is_loop_saver_pressed = False
        self.is_bank_shift_pressed = False
        self.is_mode_shift_pressed = False

        self.devices = [] # QUNEO, Reface CP
        self.messages = []
        self.threads = []
        self.control_msgs = []
        self.devices = list(set(mido.get_input_names()))
        print(self.devices)

        # LOAD SAMPLES
        self.load_all_samples()
        self.load_samples()

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
                                    if note.bank > c.MAX_SABAR_BANK_INDEX:
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
        self.all_sounds[bank_num] = new_bank
        self.pre_process_sounds(sounds = self.all_sounds[bank_num])

    def load_all_samples(self):
        self.all_sounds = []
        if c.PI_FAST_LOAD:
            max = 1
        else:
            max = 16
        for i in range(0,max): #  Load first 8 banks only
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
                self.all_sounds.append(bank)
            except FileNotFoundError:
                #print("less than 8 sample banks found")
                pass
        for bank in self.all_sounds:
            if c.PI_FAST_LOAD:
                print("PI FAST LOAD ACTIVE")
            else:
                self.pre_process_sounds(sounds = bank)

    def load_samples(self):
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
        for sound in self.sounds:

            if(c.THREADING_ACTIVE):
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

        for sound in self.all_sounds[self.current_bank]:

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
                    self.bank_shift(midi)
                    self.loop_shift(midi)
                    self.mode_shift(midi)
                if self.button_is_playable(midi):
                    self.play_sound(note.Note(None,midi,self.current_bank,port,time))
                    self.add_to_loop(midi,port,time)
                    #self.play_sound([midi],None,[self.current_bank],[port])
                if self.button_is_switch(midi):
                    self.bpm_up(midi)
                    self.bpm_down(midi)
                    self.pitch_up(midi)
                    self.pitch_down(midi)
                    self.clear_loop(midi)
                    self.record(midi)
                    self.velocity_sensitivity(midi)
                    self.exit_program(midi)
                    self.switch_bank(midi)
                    self.switch_metronome(midi)
            if midi.type == "note_off":
                if self.button_is_shift(midi):
                    self.metronome_shift(midi)
                    self.bank_shift(midi)
                    self.loop_shift(midi)
                    self.mode_shift(midi)
                if self.button_is_playable(midi):
                    if self.current_bank > c.MAX_SABAR_BANK_INDEX:
                        self.cutoff_current_sound(note.Note(None,midi,self.current_bank,port,time))
                    self.add_to_loop(midi,port,time)
            if midi.is_cc():
                self.update_mbung_vol(midi)
                self.update_col_vol(midi)
        if midi.channel == c.SYNTH_MIDI_CHANNEL:
            self.add_to_loop(midi,port,time)

            #if c.SYNTH_ONLY:


    # SHIFT FUNCTIONS - held buttons that activate selection modes

    def shift_is_active(self):
        if self.is_metronome_pressed or self.is_loop_loader_pressed or self.is_loop_saver_pressed or self.is_bank_shift_pressed\
                or self.is_mode_shift_pressed:
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

    def metronome_shift(self,midi):
        if midi.note == self.button.METRONOME:
            self.is_metronome_pressed = not self.is_metronome_pressed

    def loop_shift(self,midi):
        if midi.note == self.button.LOOP_SELECTOR:
            self.is_loop_loader_pressed = not self.is_loop_loader_pressed


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
    def pitch_up(self,midi):
        if midi.note == self.button.PITCH_UP:
            self.pitch_factor = self.pitch_factor * (1 - self.semitone)
            self.change_pitch(self.pitch_factor)
    def pitch_down(self,midi):
        if midi.note == self.button.PITCH_DOWN:
            self.pitch_factor = self.pitch_factor * (1 + self.semitone)
            self.change_pitch(self.pitch_factor)
    def clear_loop(self,midi):
        if midi.note == self.button.CLEAR_LOOP:
            print("CLEARING LOOP")
            self.metronome.midi_recorder.clear_all_loops()

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
    def switch_bank(self,midi):
        if self.is_bank_shift_pressed and midi.note in self.button.PADS:
            old_bank = self.current_bank
            self.current_bank = midi.note-self.button.PAD_START
            try:
                if c.LOAD_SAMPLES == c.ALL_SAMPLES:
                    pass
                else:
                    #  load samples as background process
                    if c.THREADING_ACTIVE:
                        x = Thread(target=self.load_samples, daemon=True)
                        x.start()
                    else:
                        self.load_samples()
            except FileNotFoundError:
                pass  # allow to be in an empty bank
                #self.current_bank = old_bank


    # PLAYABLE FUNCTIONS - if note plays a sound

    def button_is_playable(self,midi):
        if midi.note in QUNEO.PADS and not self.shift_is_active():
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
    #             for sound in self.all_sounds[self.current_bank]:
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
            if i >= 0 and i < len(self.all_sounds[entry.bank]):  # if sound has an ID

                if self.VOL_SENS:  # set volume if volume sensitivity is turned on
                    self.all_sounds[entry.bank][i].set_volume(entry.midi.velocity)
                else:
                    self.all_sounds[entry.bank][i].set_volume(128)

                if entry.bank < c.MAX_SABAR_BANK_INDEX:
                    self.cutoff_all_sounds_in_same_bank(entry) # if any sound in same bank is playing, cut it off (hand drums)

                if entry.bank >= c.MAX_SABAR_BANK_INDEX:
                    self.cutoff_current_sound(entry)  # if exact same sound is playing, cut it off

                if entry.midi.velocity>0:
                    self.all_sounds[entry.bank][i].play(block=False)  # play sound


    # def play_sound_old(self,midis,note,banks,ports):
    #     for j,midi in enumerate(midis):
    #         if c.MIDI_CONTROLLER in ports[j]:
    #             if not note:
    #                 note = midi.note
    #             i = note - self.button.PAD_START
    #             if i>=0 and i<len(self.all_sounds[banks[j]]):
    #                 if self.VOL_SENS:
    #                     self.all_sounds[banks[j]][i].set_volume(midi.velocity)
    #                 else:
    #                     self.all_sounds[banks[j]][i].set_volume(128)
    #                 if self.current_bank < 3:
    #                     for sound in self.all_sounds[banks[j]]:
    #                         sound.stop()
    #                 else:
    #                     if midi.velocity==0 or midi.type == "note_off":
    #                         self.cutoff_sound(midi)
    #                         #self.all_sounds[banks[j]][i].stop()
    #                         # for sound in self.all_sounds[banks[j]]:
    #                         #     sound.stop()
    #                 if midi.velocity>0:
    #                     self.all_sounds[banks[j]][i].play(block=False)

    # cutoff current sound
    # cutoff all sounds in same bank
    # cutoff all sounds

    def cutoff_current_sound(self,entry):
        i = entry.midi.note - self.button.PAD_START
        if i>=0 and i<len(self.all_sounds[entry.bank]): # if midi note is in bank
            self.all_sounds[entry.bank][i].stop() # stop sound

    def cutoff_all_sounds_in_same_bank(self,entry):
        i = entry.midi.note - self.button.PAD_START
        if i>=0 and i<len(self.all_sounds[entry.bank]): # if midi note is in bank
            for sound in (self.all_sounds[entry.bank]):
                sound.stop() # stop sound

    def cutoff_all_sounds(self):
        for bank in self.all_sounds:
            for sound in bank:
                sound.stop()

    def cutoff_sound(self,entry):
        i = entry.midi.note - self.button.PAD_START
        if (entry.bank > 3) and (i>=0 and i<len(self.all_sounds[entry.bank])):
            #self.sounds[i].stop()
            self.all_sounds[entry.bank][i].stop()


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
