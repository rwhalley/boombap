import pygame as pg
from time       import sleep
import numpy as np
from samplerate import resample
from scipy import signal
from threading import Thread
import CONFIG as c
#import resampy
import time

import dsp

class Soundy:

    def __init__(self,soundpath = None, fast_load = False, arr = None, no_init = False):
        self.sound_name = None
        self.bank_name = None
        self.pgsound = None
        self.original_sound = None
        self.path = soundpath
        self.pitch_factor = 1.0
        self.semitone = c.SEMITONE
        self.sample_rate = 44100
        self.repeat = False
        self.bank = None
        self.hit = None
        self.page = None
        self.pitch = 0
        self.vol = 128
        self.pgsound = None
        self.keyboard = None
        self.key_notes = []
        pg.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=128)
        pg.init()

        if not no_init:
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



    def zero_pad(self, n1,n2):
        zeros = np.zeros(n2)
        zeros[:len(n1)] = n1
        return zeros



    def apply_reverb(self):
        #3signal_arr = pg.sndarray.array(self.pgsound)
        signal_arr = pg.sndarray.array(self.pgsound)
        print(signal_arr)


        impulse_arr = pg.sndarray.array(pg.mixer.Sound('./impulse/LoveLibrary.wav'))
        print(impulse_arr)


        print(np.shape(impulse_arr))
        print(np.zeros((10,2)))

        zeros = np.zeros((10,2))
        zeros[:2] = [1,2]
        print(zeros)
        # Zero Pad
        if len(signal_arr) > len(impulse_arr):
            zeros = np.zeros((len(signal_arr),2))
            zeros[:len(impulse_arr)] = impulse_arr
            impulse_arr = zeros
        else:
            zeros = np.zeros((len(impulse_arr),2))
            zeros[:len(signal_arr)] = signal_arr
            signal_arr = zeros

        print(np.shape(signal_arr))
        print(np.shape(impulse_arr))
        print(signal_arr)
        print(impulse_arr)

        amplitudes = np.fft.rfft2(signal_arr)
        #frequencies = np.fft.rfftfreq(len(signal_arr), 1 / self.sample_rate)

        iamp = np.fft.rfft2(impulse_arr)
        #ifreq = np.fft.rfftfreq(len(impulse_arr), 1 / self.sample_rate)
        print(amplitudes)
        print(iamp)


        # convolution
        convo = (amplitudes * iamp)
        print(convo)
        convo = np.fft.irfft2(convo)
        print("convo")
        print(convo)
        # Readjust maxed out amplitudes
        if np.max(convo) > 1 or np.min(convo) < -1:
            print(abs(np.min(convo)))
            print(max(abs(np.max(convo)), abs(np.min(convo))))
            convo = convo / max(abs(np.max(convo)), abs(np.min(convo)))

        convo= (convo * (32767)).astype(np.int16)


        # mix dry/wet
        convo = ((0.5*convo + 0.5*signal_arr).astype(np.int16))





        self.pgsound=pg.sndarray.make_sound(convo)
        self.normalize()

        #a = (np.array([signal.fftconvolve(signal_arr[:],impulse_arr[:],mode='same')], np.int16)[0])

        #print(np.array([dsp.convolution_reverb(signal_arr[:],impulse_arr[:])], np.int16)[0])

        #self.pgsound = pg.sndarray.make_sound(np.array([signal.fftconvolve(impulse_arr[:],signal_arr[:],mode='same')], np.int16)[0])

        #self.pgsound = pg.sndarray.make_sound(np.array([dsp.convolution_reverb(signal_arr[:],impulse_arr[:])], np.int16)[0])


    def get_original_sound_array(self):
        try:
            return np.array(pg.sndarray.array(self.pgsound), np.int16)
        except TypeError:
            pass

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

    # use internally for keyboard creation
    def make_keyboard(self,start_semitone=0, num_keys=13, reload=False):
        if self.keyboard and not reload:
            print("Keyboard already loaded.")
        else:
            self.keyboard = [None] * num_keys
            self.key_notes = []
            self.pitch_factors = []
            for i in range(0,num_keys):
                pitch_in_semitones = (start_semitone-i)
                print(f"i: {i}")
                print(f"start_semitone: {start_semitone}")
                print(f"pitch_in_semitones: {pitch_in_semitones}")


                pitch_factor = 2**(pitch_in_semitones/12)#(1 + c.SEMITONE)**pitch_in_semitones
                #pitch_factor = 2

                    #pitch_factor = 2**(pitch_in_semitones/12)#(1 - c.SEMITONE)**(-pitch_in_semitones)
                print(f"pitch_factor: {pitch_factor}")
                self.keyboard[i] = (pg.sndarray.make_sound(resample(pg.sndarray.array(self.original_sound),pitch_factor,'sinc_fastest').astype(dtype="int16")))
                self.key_notes.append(i)
                self.pitch_factors.append(pitch_factor)
            print(self.keyboard)
            print(self.key_notes)
            print(self.pitch_factors)

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

    def play(self, block = False, lvol = 1.0, rvol = 1.0, key=None):
        #self.pgsound.set_volume(lvol)

        if key or key == 0:
            self.keyboard[key].play()
        else:
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

    def stop(self, key=None):
        #self.pgsound.fadeout(25)
        if key or key == 0:
            self.keyboard[key].stop()
        else:
            try:
                self.pgsound.stop()
            except AttributeError:
                pass
                #print("empty_sample")

# s = Soundy(soundpath='./samples/2/04_tet_oh.aif_loud.wav')
# s.apply_reverb()
# s.play(block=False)
# time.sleep(10)



# import matplotlib.pyplot as plt
# fig, (ax_orig, ax_mag) = plt.subplots(2, 1)
# ax_orig.plot(sig)
# ax_orig.set_title('White noise')
# ax_mag.plot(np.arange(-len(sig)+1,len(sig)), autocorr)
# ax_mag.set_title('Autocorrelation')
# fig.tight_layout()
# fig.show()
