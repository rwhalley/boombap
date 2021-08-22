#!/usr/bin/python
import rtmidi as rtmidi
from soundy_pygame import Soundy
from os import listdir
from os.path import isfile, join
from threading import Thread
from metronome import Metronome
import sys
from pathlib import Path
import QUNEO

from midiparse import MIDIParse as mp
import CONFIG as c

try:
    import alsaaudio
    print("Linux OS")
except:
    print("Non-Linux OS")

class MidiControl:

    def __init__(self):

        self.basepath = str(Path(__file__).parent / 'samples/')+'/'
        self.current_bank = 0
        self.max_sample_length_seconds = 3
        self.max_bank_size = 16
        self.button = QUNEO

        #if c.LOAD_SAMPLES == c.ALL_SAMPLES:
        self.load_all_samples()
        #else:
        self.load_samples()

        self.metronome_path = Path(__file__).parent.resolve() / 'metronome/metronome.wav'
        self.metronome = Metronome(bpm=120,path=self.metronome_path, controller=self)
        self.VOL_SENS = False
        self.port_name = None
        self.ports = []

        # --- Shift Buttons ---
        self.is_metronome_pressed = False
        self.is_loop_selector_pressed = False
        self.is_bank_shift_pressed = False

        self.devices = [rtmidi.MidiIn(),rtmidi.MidiIn()] # QUNEO, Reface CP
        ports = self.devices[0].get_ports()
        if ports:
            for i,port in enumerate(ports):
                print(self.devices[0].get_port_name(i))
                self.ports.append(port)
                self.devices[i].open_port(i)


            while True:
                self.metronome.get_time()

                messages = []

                for device in self.devices:
                    try:
                        messages.append(device.get_message()) # some timeout in ms
                    except:
                        messages.append(None)

                for i, message in enumerate(messages):
                    if message:
                        self.print_message(message,ports[i])


        else:
            print('NO MIDI INPUT PORTS!')

    def return_self(self):
        print("RETURNING SELF")
        return self

    def load_all_samples(self):
        self.all_sounds = []
        for i in range(0,16): #  Load first 8 banks only
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
                print("less than 8 sample banks found")
                pass
        for bank in self.all_sounds:
            self.pre_process_sounds(sounds = bank)


    def load_samples(self):
        path = self.basepath + str(self.current_bank)+'/'
        onlyfiles = [f for f in sorted(listdir(path)) if isfile(join(path, f))]
        self.sounds = []
        for file in onlyfiles:
            if file.endswith('.wav'):
                if file.startswith('.'):
                    pass
                else:
                    self.sounds.append(Soundy(path+file))
        self.sounds = self.sounds[0:self.max_bank_size]
        self.pre_process_sounds()


    def pre_process_sounds(self, sounds = None):
        if not sounds:
            sounds = self.sounds
        for sound in sounds:
            sound.restrict_length(self.max_sample_length_seconds)  # Truncate Samples longer than n seconds
            sound.remove_artifacts()
            sound.normalize()
            sound.make_loud()

    def switch_vol_sens(self):
        self.VOL_SENS = not self.VOL_SENS
        #print(self.VOL_SENS)

    def adjust_volume(self, turn_up):
        try:
            m = alsaaudio.Mixer()
            current_volume = m.getvolume()
            #print(current_volume)
            if turn_up:
                new_volume = current_volume[0]+10
            else:
                new_volume = current_volume[0]-10
            if new_volume<0:
                new_volume = 0
            elif new_volume>100:
                new_volume = 100
            m.setvolume(new_volume)
        except ImportError:
            print("Volume Adjustment Not Available for Non-Linux")
            pass



    def play_sound(self,midis,note,banks):
        for j,midi in enumerate(midis):

            #print("PLAY_SOUND")
            #print(midi)
            if not note:
                #print("GET NOTE")
                note = mp.getNoteNumber(midi)
                #print(note)
            i = note - self.button.PAD_START
            print(i)
            if i<0:
                raise IndexError
            if self.current_bank < 4:
                for sound in self.all_sounds[banks[j]]:
                    sound.stop()
            if self.VOL_SENS:
                self.all_sounds[banks[j]][i].set_volume(mp.getVelocity(midi))
            else:
                self.all_sounds[banks[j]][i].set_volume(128)
            self.all_sounds[banks[j]][i].play(block=False)


    def print_message(self,midi,port):
        try:
            note = mp.getNoteNumber(midi)
            #print(f"note = {note}")

            if mp.isNoteOn(midi):

                if note == 17:
                    print("WHATSS")
                if note == self.button.SAVE_LOOP:
                    print("UPPP")
                if note != self.button.METRONOME and note != self.button.CLEAR_LOOP:

                    try:
                        if self.metronome.midi_recorder.RECORD:
                            self.metronome.midi_recorder.add_entry(midi,port)
                            print("ADDED")
                            print(self.metronome.midi_recorder.my_loop)
                    except:
                        pass

                    # --- ACTIVATE METRONOME RHYTHM SELECTOR ---
                    if self.is_metronome_pressed and note in self.button.PADS:
                        self.metronome.switch(note-self.button.PAD_START)

                    # --- ACTIVATE LOOPER PATTERN SELECTOR ---
                    if self.is_loop_selector_pressed and note in self.button.PADS:
                        try:
                            self.metronome.midi_recorder.my_loop = self.metronome.midi_recorder.my_loops[note-self.button.PAD_START]
                        except IndexError:
                            print("Loop index not found: Add more loops.")
                            pass

                    # --- ACTIVATE BANK SELECTION ---
                    if self.is_bank_shift_pressed and note in self.button.PADS:
                        old_bank = self.current_bank
                        self.current_bank = note-self.button.PAD_START
                        try:
                            if c.LOAD_SAMPLES == c.ALL_SAMPLES:
                                pass
                            else:
                                #  load samples as background process
                                x = Thread(target=self.load_samples, daemon=True)
                                x.start()
                        except FileNotFoundError:
                            self.current_bank = old_bank

                    if note == self.button.SAVE_LOOP:
                        print("SAVE LOOP BUTTON PRESSED")

                    # --- Save Current Loop to Memory ---
                    if self.is_loop_selector_pressed and note == self.button.SAVE_LOOP:
                        print("SAVING LOOP")
                        self.metronome.midi_recorder.save_loop()


                    # --- Select Loop from Saved Loops ---
                    if self.is_loop_selector_pressed and note in self.button.PADS:

                        selection_index = note-self.button.PAD_START
                        print(f"SELECTING LOOP {str(selection_index)}")
                        self.metronome.midi_recorder.my_loop = self.metronome.midi_recorder.my_loops[selection_index]




                try:  # PLAY SOUND

                    i = note - self.button.PAD_START
                    if i<0:
                        raise IndexError
                    if self.current_bank < 4:
                        for sound in self.sounds:
                            sound.stop()
                        for sound in self.all_sounds[self.current_bank]:
                            sound.stop()
                    if self.VOL_SENS:
                        self.sounds[i].set_volume(mp.getVelocity(midi))
                    else:
                        self.sounds[i].set_volume(128)
                    self.sounds[i].play(block=False)


                    ### OLD CONTROLS
                except:

                    if note == self.button.METRONOME:
                        self.is_metronome_pressed = True
                        #self.metronome.switch()

                    #elif self.is_metronome_pressed and note in self.button.PADS:

                        #self.metronome.midi_player.play_note(midi)

                    #    self.metronome.switch(note-self.button.PAD_START)

                    # --- Activate Shift Button For Sample Bank Selection ---
                    elif note == self.button.BANK_SELECTOR:
                        # self.is_bank_shift_pressed = True
                        # print("bank on")
                        self.is_bank_shift_pressed = not self.is_bank_shift_pressed
                        if self.is_bank_shift_pressed:
                            print("bank on")
                        else:
                            print("bank off")



                    # --- Activate Shift Button For Loop Functions ---
                    elif note == self.button.LOOP_SELECTOR:
                        print("loop on")
                        self.is_loop_selector_pressed = True





                    elif note == self.button.BANK_UP:
                        self.current_bank += 1
                        try:
                            if c.LOAD_SAMPLES == c.ALL_SAMPLES:
                                pass
                            else:
                                #  load samples as background process
                                x = Thread(target=self.load_samples, daemon=True)
                                x.start()
                        except FileNotFoundError:
                            self.current_bank -= 1

                    elif note == self.button.BANK_DOWN:
                        self.current_bank -= 1
                        try:
                            if c.LOAD_SAMPLES == c.ALL_SAMPLES:
                                pass
                            else:
                                #  load samples as background process
                                x = Thread(target=self.load_samples, daemon=True)
                                x.start()
                        except FileNotFoundError:
                            self.current_bank += 1

                    elif note == self.button.EXIT:
                        try:
                            if "reface CP" in self.ports:
                                self.metronome.midi_player.all_notes_off()
                            self.metronome.midi_player.cleanup()
                        except:
                            pass
                        sys.exit()

                    elif note == self.button.VOL_UP:
                        self.adjust_volume(True)  # Turn Volume Up

                    elif note == self.button.VOL_DOWN:
                        self.adjust_volume(False)  #Turn Volume Down

                    elif note == self.button.CLEAR_LOOP:
                        if "reface CP" in self.ports:
                            self.metronome.midi_player.all_notes_off()
                        self.metronome.midi_recorder.clear_current_loop()

                    elif note == self.button.RECORD:
                        self.metronome.midi_recorder.switch_record_button()



            elif mp.isNoteOff(midi):


                # CUT OFF SOUND

                if(note != self.button.METRONOME):
                    if port == "reface CP":  # Don't care about the off notes for now for QUNEO
                        try:
                            if self.metronome.midi_recorder.RECORD:
                                self.metronome.midi_recorder.add_entry(midi,port)
                            #print("OFF_ADDED")
                            #print(self.metronome.midi_recorder.my_loop)
                        except:
                            pass

                i = note - self.button.PAD_START

                if self.current_bank > 3:
                    self.sounds[i].stop()

                if note == self.button.VELOCITY_SENSITIVITY:
                    self.switch_vol_sens()

                if note == self.button.METRONOME:
                    self.is_metronome_pressed = False

                # # --- Deactivate Shift Button For Sample Bank Selection ---
                # if note == self.button.BANK_SELECTOR:
                #    print("bank off")
                #    self.is_bank_shift_pressed = False

                # --- Deactivate Shift Button For Loop Functions ---
                elif note == self.button.LOOP_SELECTOR:
                    print("loop off")
                    self.is_loop_selector_pressed = False

            elif mp.isController(midi):
                #print(f"controller = {midi.getControllerValue()}")

                if(mp.getNoteNumber(midi) == self.button.PITCH_CONTROL):
                    for sound in self.sounds:
                        factor = 1.5 - mp.getControllerValue(midi)/128.
                        print(factor)

                        # Run DSP as background process
                        x = Thread(sound.change_pitch(factor), daemon=True)
                        x.start()
                        x = Thread(sound.normalize(), daemon=True)
                        x.start()
                        x = Thread(sound.make_loud(), daemon=True)
                        x.start()
                    for sound in self.all_sounds[self.current_bank]:
                        factor = 1.5 - mp.getControllerValue(midi)/128.
                        print(factor)

                        # Run DSP as background process
                        x = Thread(sound.change_pitch(factor), daemon=True)
                        x.start()
                        x = Thread(sound.normalize(), daemon=True)
                        x.start()
                        x = Thread(sound.make_loud(), daemon=True)
                        x.start()

                elif note == self.button.BPM_CONTROL:
                    print(mp.getControllerValue(midi))
                    self.metronome.set_bpm(mp.getControllerValue(midi)/128.)

                elif note == self.button.MBUNG_VOL_CONTROL:  # mbungmbung volume
                    drum = 0
                    self.metronome.update_volume(drum,mp.getControllerValue(midi))

                elif note == self.button.COL_VOL_CONTROL:  # col volume
                    drum = 1
                    self.metronome.update_volume(drum,mp.getControllerValue(midi))


                #print('CONTROLLER', midi.getControllerNumber(), midi.getControllerValue())
        except IndexError:
            pass


MidiControl()
