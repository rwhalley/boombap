import moviepy.editor as mp
import os
import skvideo.io

from scipy.io.wavfile import read, write
import pygame
from soundy_pygame import Soundy
import time
from onset_detect import get_onsets
import CONFIG as c
import numpy as np




class vSlicer:

    def __init__(self):
        self.is_playing = False
        self.vfilename = c.VIDEO_INPUT_PATH+ os.listdir(c.VIDEO_INPUT_PATH)[0]
        self.afilename = c.VIDEO_TEMP_PATH+"my_audio.wav"
        self.samplerate = 44100
        self.slicepoints = []
        self.t0 = None
        self.dimensions = None
        self.vframerate_str = None
        # import movie
        # extract sound from movie


    def load_audio(self):
        audioclip = mp.AudioFileClip(self.vfilename)
        audioclip.write_audiofile(self.afilename)

        #anp = read(self.afilename)  # audio as numpy
        self.aplay = Soundy(self.afilename) # audio in pygame


    def start_play(self):
        # start timer
        self.t0 = time.time()
        self.is_playing = True
        # play sound
        self.aplay.play()



    def end_play(self):
        self.is_playing = False


        # turn on midi collection
    def add_slicepoint(self):
        # acquire midi slicepoints
        print(f"adding timepoint: {(time.time()-self.t0)}")
        self.slicepoints.append((time.time()-self.t0))


    def process_slicepoints(self):

        fp = [int(x*self.samplerate) for x in self.slicepoints] # the midi inputs as framepoints

        sl = 4*self.samplerate # sample length is 2 seconds

        # we want audio slices that are 0.5 second time window (wl) before and after
        wl = self.samplerate//2  # (0.5 seconds)

        self.samplerate, self.adata = read(self.afilename)
        print(self.afilename)
        print(f"sr{self.samplerate}")
        print(self.adata)
        aslices = []
        print(f"fp {fp}")
        for i, x in enumerate(fp):
            aslices.append(self.adata[(x):((x)+sl)])
        #aslices = [self.adata[(x-wl):((x-wl)+sl)] for x in fp]

        #TODO for fun, consider doing in place operations instead of making new lists

        # get onsets that are near the slicepoints +/- 0.5 seconds
        # run onset detection
        self.onsets = []
        for i,aslice in enumerate(aslices):
            print(aslice)
            raw_o = get_onsets(None,w=aslice,sr=self.samplerate)
            self.onsets.append(raw_o[0]+self.slicepoints[i]) # append the first onset for each slice to the list of onsets


        print(f"ONSETS {self.onsets}")
        # post-process onsets
        #onsets = self.zero_any_negatives(self.left_shift_onsets(self.remove_close_onsets(self.onsets),0.03))



    def slice_video(self):
        # load video as numpy
        self.vmeta = skvideo.io.ffprobe(self.vfilename)['video']
        print(self.vmeta)
        self.vframerate_str = self.vmeta['@avg_frame_rate']
        self.vframerate = (float(self.vmeta['@nb_frames'])/float(self.vmeta['@duration']))
        self.vdata = skvideo.io.vread(self.vfilename, inputdict={'-r' : str(int(self.vframerate))})

        self.dimensions = str(self.vdata.shape[2])+"x"+str(self.vdata.shape[1])


        #self.vframerate = 30 # int(vmeta['video']['@avg_frame_rate'][0:2])

        # slice video
        print(f"vframerate {self.vframerate}")
        vsliceindices = [int(i * self.vframerate) for i in self.onsets]
        print(f"vsliceindices {vsliceindices}")

        self.voutputs = []
        print(f"len vdata: {len(self.vdata)}")

        for si in vsliceindices:  # for each end index
            print(f"si {si}")
            if (c.APPLY_START_OFFSET):
                offset = int(c.START_OFFSET_S * self.vframerate)
            else:
                offset = 0

            ei = int(si + c.SLICE_LENGTH*self.vframerate) # end index is 1 second post start index
            print(f"ei  {ei}")
            start = 0
            if (si+offset) < 0:
                start = 0
            else: start = si+offset
            print(self.vdata[(si+offset):ei])

            self.voutputs.append(self.vdata[start:ei])

    def slice_audio(self):
        # slice audio
        asliceindices = [int(i * self.samplerate) for i in self.onsets]


        self.aoutputs = []
        for si in asliceindices:
            ei = int(si + c.SLICE_LENGTH*self.samplerate)
            self.aoutputs.append(self.adata[si:ei])

    def export_audio(self,kitnum):
        # send audio and video to folders

        afolder = c.USB + c.RECORDED_SAMPLES_FOLDER + '/'+str(kitnum)+'/'
        print(f"writing new audio samples to file")
        print(f"aoutputs {len(self.aoutputs)}")
        for i,sound in enumerate(self.aoutputs):
            write(afolder+"{:02d}".format(i)+".wav",self.samplerate,sound)


    def export_video(self):
        vfolder = c.VIDEO_OUTPUT_PATH
        for i,video in enumerate(self.voutputs):
            print(f"writing new videio samples to file")
            print(video)
            skvideo.io.vwrite(vfolder+"{:02d}".format(i)+".mp4",video, inputdict={'-r' : self.vframerate_str})#str(int(self.vframerate))})#, outputdict={'-s' : self.dimensions})

    def cleanup(self):
        del self.voutputs
        self.voutputs = None
        del self.vdata
        self.vdata = None
        del self.adata
        self.adata = None
        del self.aoutputs
        self.aoutputs = None

#
# filename = "trying.mp4"
#
# vclip = mp.VideoFileClip("trying.mp4")
# aclip = mp.AudioFileClip("trying.mp4")
# print(aclip.get_frame(0).shape)
# print(vclip.get_frame(0).shape)
# print(aclip.to_soundarray)
#print([frame for frame in aclip.iter_frames()])


#mp.VideoFileClip(videopath).set_audio(mp.AudioFileClip(audiopath)).write_videofile("trying.mp4")
