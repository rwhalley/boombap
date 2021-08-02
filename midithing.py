#!/usr/bin/python
import rtmidi as rtmidi
from soundy_pygame import Soundy
from os import listdir
from os.path import isfile, join
from threading import Thread
from metronome import Metronome
import sys
from pathlib import Path

from midiparse import MIDIParse as mp

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
        self.load_samples()
        self.metronome_path = Path(__file__).parent.resolve() / 'metronome/metronome.wav'
        self.metronome = Metronome(120,path=self.metronome_path)
        self.VOL_SENS = False


        midiin = rtmidi.MidiIn()
        ports = midiin.get_ports()
        if ports:
            for i,port in enumerate(ports):
                print(midiin.get_port_name(i))
            print("Opening port 0!")
            midiin.open_port(0)
            while True:
                self.metronome.get_time()

                m = midiin.get_message() # some timeout in ms
                if m:
                    self.print_message(m)
        else:
            print('NO MIDI INPUT PORTS!')



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
        for sound in self.sounds:
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


    def print_message(self,midi):
        try:
            note = mp.getNoteNumber(midi)
            print(f"note = {note}")


            if mp.isNoteOn(midi):
                # try:
                #     if self.metronome.midi_recorder.RECORD:
                #         self.metronome.midi_recorder.add_entry(midi)
                #     print("ADDED")
                #     print(self.metronome.midi_recorder.my_loop)
                # except:
                #     pass
                #if note != 22 and note !=23 and note!=26 and note != 24 and note != 20 and note != 21:

                try:
                    i = note-36
                    if i<0:
                        raise IndexError
                    if self.current_bank < 4:
                        for sound in self.sounds:
                            sound.stop()
                    if self.VOL_SENS:
                        self.sounds[i].set_volume(mp.getVelocity(midi))
                    else:
                        self.sounds[i].set_volume(128)
                    self.sounds[i].play(block=False)

                except:
                    if note == 26:
                        #self.metronome.midi_player.play_note(midi)
                        self.metronome.switch()
                    elif note == 22:
                        self.current_bank += 1
                        try:
                            self.load_samples()
                        except FileNotFoundError:
                            self.current_bank -= 1
                    elif note == 23:
                        self.current_bank -= 1
                        try:
                            self.load_samples()
                        except FileNotFoundError:
                            self.current_bank += 1
                    elif note ==24:
                        try:
                            self.metronome.midi_player.cleanup()
                        except:
                            pass
                        sys.exit()
                    elif note == 20:
                        self.adjust_volume(True)  # Turn Volume Up
                    elif note == 21:
                        self.adjust_volume(False)  #Turn Volume Down




            elif mp.isNoteOff(midi):
                # try:
                #     if self.metronome.midi_recorder.RECORD:
                #         self.metronome.midi_recorder.add_entry(midi)
                #     print("ADDED")
                #     print(self.metronome.midi_recorder.my_loop)
                # except:
                #     pass
                i = mp.getNoteNumber(midi)-36
                if self.current_bank > 3:
                    self.sounds[i].stop()
                if note ==25:
                    self.switch_vol_sens()
            elif mp.isController(midi):
                #print(f"controller = {midi.getControllerValue()}")
                if(mp.getNoteNumber(midi) == 10):
                    for sound in self.sounds:
                        factor = 1.5 - mp.getControllerValue(midi)/128.
                        print(factor)
                        x = Thread(sound.change_pitch(factor))
                        x.start()
                        sound.normalize()
                        sound.make_loud()

                elif note == 6:
                    print(mp.getControllerValue(midi))
                    self.metronome.set_bpm(mp.getControllerValue(midi)/128.)
                elif note == 0:  # mbungmbung volume
                    drum = 0
                    self.metronome.update_volume(drum,mp.getControllerValue(midi))
                elif note == 1:  # col volume
                    drum = 1
                    self.metronome.update_volume(drum,mp.getControllerValue(midi))


                #print('CONTROLLER', midi.getControllerNumber(), midi.getControllerValue())
        except IndexError:
            pass


MidiControl()
