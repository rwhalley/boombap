import pygame as pg
from time       import sleep
import numpy as np
from samplerate import resample
from scipy import signal
from threading import Thread
#import resampy
import sounddevice as sd
import soundfile as sf

class Soundy:

    def __init__(self,soundpath):
        self.sample_rate = 44100
        # Extract data and sampling rate from file
        self.data, self.fs = sf.read(soundpath, dtype='float32')
        self.play()
        #status = sd.wait()  # Wait until file is done playing
        #self.pgsound = pg.mixer.Sound(soundpath)
        #self.original_sound = pg.mixer.Sound(soundpath)

    def restrict_length(self,len_in_seconds):
        sleep(1000)
        self.pgsound = pg.sndarray.make_sound(pg.sndarray.array(self.pgsound)[:int(self.sample_rate*len_in_seconds),:])



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
        snd_array = pg.sndarray.array(self.original_sound)
        #factor = int(len(snd_array)*factor)
        #snd_resample = resampy.resample(snd_array,self.sample_rate, int(self.sample_rate*factor) - int(self.sample_rate*factor)%128 ,axis=0)
        #snd_resample = signal.resample(snd_array,factor).astype(snd_array.dtype)
        snd_resample=resample(snd_array,factor,'sinc_fastest').astype(snd_array.dtype)
        self.pgsound = pg.sndarray.make_sound(snd_resample)

    def set_volume(self,midi_vel_in):
        normalized_vel = midi_vel_in/128.
        self.pgsound.set_volume(normalized_vel)

    def play(self):
        sd.play(self.data, self.fs, blocking=False)




    def stop(self):
        #self.pgsound.fadeout(200)
        self.pgsound.stop()
