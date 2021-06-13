#!/usr/bin/python
import rtmidi
from soundy_pygame import Soundy
from os import listdir
from os.path import isfile, join
from threading import Thread
from metronome import Metronome
import sys
from pathlib import Path

class MidiControl:

    def __init__(self):

        self.basepath = str(Path(__file__).parent / 'samples/')+'/'
        self.current_bank = 0
        self.max_sample_length_seconds = 3
        self.max_bank_size = 16
        self.load_samples()
        self.metronome_path = Path(__file__).parent.resolve() / 'metronome/metronome.wav'
        self.metronome = Metronome(120,path=self.metronome_path)


        midiin = rtmidi.RtMidiIn()
        ports = range(midiin.getPortCount())
        if ports:
            for i in ports:
                print(midiin.getPortName(i))
            print("Opening port 0!")
            midiin.openPort(0)
            while True:
                self.metronome.get_time()
                m = midiin.getMessage(10) # some timeout in ms
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

    def print_message(self,midi):
        try:
            #print('ON: ', midi.getMidiNoteName(midi.getNoteNumber()), midi.getVelocity())
            note = midi.getNoteNumber()

            print(note)
            if midi.isNoteOn():

                if note != 22 and note !=23 and note!=26:
                    i = note-36
                    if (i==12):
                        sys.exit()
                    for sound in self.sounds:
                        sound.stop()
                    #self.sounds[i].set_volume(midi.getVelocity())
                    self.sounds[i].play(block=False)

                else:
                    if note == 26:
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


            elif midi.isNoteOff():
                #print('OFF:', midi.getMidiNoteName(midi.getNoteNumber()))
                i = midi.getNoteNumber()-36
                #self.sounds[i].stop()
            elif midi.isController():
                if(midi.getNoteNumber() == 10):
                    for sound in self.sounds:
                        factor = 1.5 - midi.getControllerValue()/128.
                        print(factor)
                        x = Thread(sound.change_pitch(factor))
                        x.start()
                        sound.normalize()
                        sound.make_loud()

                elif note == 6:
                    self.metronome.set_bpm(midi.getControllerValue()/128.)


                #print('CONTROLLER', midi.getControllerNumber(), midi.getControllerValue())
        except IndexError:
            pass


MidiControl()
