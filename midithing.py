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

        self.is_metronome_pressed = False


        midiin = rtmidi.MidiIn()
        ports = midiin.get_ports()
        if ports:
            for i,port in enumerate(ports):
                print(midiin.get_port_name(i))

            self.port_name = ports[0]
            print("Opening port 0!")
            midiin.open_port(0)
            while True:
                self.metronome.get_time()

                m = midiin.get_message() # some timeout in ms
                if m:
                    self.print_message(m)
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


    def print_message(self,midi):
        try:
            note = mp.getNoteNumber(midi)
            #print(f"note = {note}")

            if mp.isNoteOn(midi):

                if note != self.button.METRONOME and note != self.button.CLEAR_LOOP:

                    try:
                        if self.metronome.midi_recorder.RECORD:
                            self.metronome.midi_recorder.add_entry(midi)
                            #print("ADDED")
                            #print(self.metronome.midi_recorder.my_loop)
                    except:
                        pass

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

                    if self.is_metronome_pressed and note in self.button.PADS:
                        print("METRENOME PRESSED")
                        print(note-self.button.PAD_START)
                        self.metronome.switch(note-self.button.PAD_START)

                except:
                    print(note)
                    print(note== self.button.METRONOME)
                    if note == self.button.METRONOME:
                        self.is_metronome_pressed = True
                        #self.metronome.midi_player.play_note(midi)
                        #self.metronome.switch()


                    elif self.is_metronome_pressed and note in self.button.PADS:
                        self.metronome.switch(note-self.button.PAD_START)

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
                            self.metronome.midi_player.cleanup()
                        except:
                            pass
                        sys.exit()

                    elif note == self.button.VOL_UP:
                        self.adjust_volume(True)  # Turn Volume Up

                    elif note == self.button.VOL_DOWN:
                        self.adjust_volume(False)  #Turn Volume Down

                    elif note == self.button.CLEAR_LOOP:
                        self.metronome.midi_recorder.clear_current_loop()

                    elif note == self.button.RECORD:
                        self.metronome.midi_recorder.switch_record_button()




            elif mp.isNoteOff(midi):

                if(note != self.button.METRONOME):
                    if self.port_name != "QUNEO":  # Don't care about the off notes for now for QUNEO
                        try:
                            if self.metronome.midi_recorder.RECORD:
                                self.metronome.midi_recorder.add_entry(midi)
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
