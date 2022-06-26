import pygame as pg
from time       import sleep
import numpy as np
from samplerate import resample
from scipy import signal
from threading import Thread
#import resampy

import dsp

class Soundy:

    def __init__(self,soundpath = None, fast_load = False, arr = None):
        self.sound_name = None
        self.bank_name = None
        self.pgsound = None
        self.original_sound = None
        self.path = soundpath
        self.pitch_factor = 1.0
        self.sample_rate = 44100
        self.repeat = False
        self.bank = None
        self.hit = None
        self.page = None
        self.pitch = 0
        pg.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=64)
        pg.init()

        if fast_load:
            self.pgsound = pg.sndarray.make_sound(arr)
            self.original_sound = pg.sndarray.make_sound(arr)
        else:
            self.pgsound = pg.mixer.Sound(soundpath)
            self.original_sound = pg.mixer.Sound(soundpath)

    def restrict_length(self,len_in_seconds):
        self.pgsound = pg.sndarray.make_sound(pg.sndarray.array(self.pgsound)[:int(self.sample_rate*len_in_seconds),:])

    def normalize(self):
        snd_array = pg.sndarray.array(self.pgsound)
        self.pgsound = pg.sndarray.make_sound(np.array([(snd_array / np.max(np.abs(snd_array))) * 32767], np.int16)[0])

    def make_loud(self):
        snd_array = pg.sndarray.array(self.pgsound)

        #print(dsp.arctan_compressor(dsp.limiter(snd_array[:])))
        self.pgsound = pg.sndarray.make_sound(np.array([dsp.limiter(snd_array[:])], np.int16)[0])
        #print(np.array([dsp.arctan_compressor(dsp.limiter(snd_array[:]))], np.int16)[0])


    def get_original_sound_array(self):
        return np.array(pg.sndarray.array(self.pgsound), np.int16)

    def remove_artifacts(self):

        snd_array = pg.sndarray.array(self.pgsound)

        # --- REMOVE SILENCE AT BEGINNING OF SAMPLES ---
        sound_start = None
        for i, sample in enumerate(snd_array):
            if abs(sample.sum()) > 150:
                sound_start = i
                break
        if sound_start:
            snd_array = snd_array[sound_start:,:]

        # --- FADE BEGINNING AND END OF SAMPLE TO REMOVE HIGH FREQUENCY ARTIFACTS ---
        #fade = 200. # Fade in MS
        #fade_in = np.arange(0., 1., 1/fade)
        #fade_in = fade_in*fade_in
        #fade_out = np.arange(1., 0., -1/fade)
        #fade = int(fade)
        #for i in range (0,2):
        #    snd_array[:fade,i] = np.multiply(snd_array[:fade,i], fade_in)
        #    snd_array[-fade:,i] = np.multiply(snd_array[-fade:,i], fade_out)

        # --- SET NEW DEFAULT SOUND AFTER PROCESSING ---
        self.pgsound = pg.sndarray.make_sound(snd_array)
        self.original_sound=self.pgsound


    def lowpass_filter(self):
        N=5
        Wn=0.1
        B,A = signal.butter(N,Wn,output='ba')
        snd_array = pg.sndarray.array(self.pgsound)
        for i in range (0,2):
            snd_array[:,i] = signal.filtfilt(B,A,snd_array[:,i])
        self.pgsound = pg.sndarray.make_sound(snd_array)

    def change_pitch(self,factor):
        self.pitch_factor = self.pitch_factor*factor
        snd_array = pg.sndarray.array(self.original_sound)  # Change from original reference sound to avoid sample degeneration
        #factor = int(len(snd_array)*factor)
        #snd_resample = resampy.resample(snd_array,self.sample_rate, int(self.sample_rate*factor) - int(self.sample_rate*factor)%128 ,axis=0)
        #snd_resample = signal.resample(snd_array,factor).astype(snd_array.dtype)
        snd_resample=resample(snd_array,self.pitch_factor,'sinc_fastest').astype(snd_array.dtype)
        self.pgsound = pg.sndarray.make_sound(snd_resample)

    def set_volume(self,midi_vel_in):
        normalized_vel = midi_vel_in/128.
        self.pgsound.set_volume(normalized_vel)

    # def set_volume_stereo(self,left,right):
    #     self.pgsound.set_volume(left,right)

    def play(self, block = True, lvol = 1.0, rvol = 1.0):
        self.pgsound.set_volume(lvol)
        self.pgsound.play()
        # channel = self.pgsound.play()
        # channel.set_volume(lvol,rvol)

        if(self.repeat):
            sleep(0.1)
            self.pgsound.play()
            sleep(0.1)
            self.pgsound.play()

        if block:
            sleep(self.nssound.duration())

    def stop(self):
        #self.pgsound.fadeout(25)
        self.pgsound.stop()
