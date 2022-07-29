#from librosa import load
#from librosa.onset import onset_detect

import numpy as np
import soundfile as sf
import os
import glob
from datetime import datetime as dt
from onset_detect import get_onsets

import CONFIG as c

class Slicer:
    def __init__(self,input_wav_file, pre_slice,folder_num):
        self.path = c.USB + '11 - Jungle/'+str(folder_num)+'/' #'./samples/'+str(folder_num)+'/'
        self.old_files_path = './oldsamples/' + str(dt.now().strftime("%y%m%d%H%M%S"))+"/"
        self.input_wav_file = input_wav_file
        self.pre_slice = pre_slice
        #if int(folder_num)>7:
        self.slice_samples()
        #self.delete_files_in_folder('./samples/'+str(folder_num)+'/*')




    def slice_samples(self):
        if not self.folder_has_files(self.path):  # If there
            self.create_new_folder(self.path)
        else:
            self.create_new_folder(self.old_files_path)
            self.move_files_to_folder(self.path,self.old_files_path)

        self.sample_rate =44100
        print(self.input_wav_file)
        self.input_wav = sf.read(self.input_wav_file)# None, None #load(self.input_wav_file)
        print(self.input_wav)
        self.max_onsets = 16
        self.onsets = [] #onset_detect(y=self.input_wav, sr=self.sample_rate, units='samples',wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
        self.sliced =[ ]
        self.onsets = get_onsets(self.input_wav_file)
        print(self.onsets)
        self.onsets = self.zero_any_negatives(self.left_shift_onsets(self.remove_close_onsets(self.onsets),0.03))

        print(self.onsets)
        #self.onsets = self.zero_any_negatives(self.left_shift_onsets(self.remove_close_onsets(self.onsets),0.050))

        start_index = (self.sample_rate*self.pre_slice[0])
        end_index =(self.sample_rate*self.pre_slice[1])
        self.input_wav = self.input_wav[start_index:end_index]
        for i,onset in enumerate(self.onsets):
            if i==16:
                break
            else:
                data = None
                if i< (len(self.onsets)-1):
                    data =(self.input_wav[0][int(onset*self.sample_rate):int(self.onsets[i+1]*self.sample_rate)])

                elif i == (len(self.onsets)-1):
                     data = self.input_wav[0][int(onset*self.sample_rate):(len(self.input_wav[0])-1)]
                if hasattr(data, 'shape'):
                    sf.write(self.path+str(i)+'.wav', data, self.sample_rate, subtype='PCM_16')


    def left_shift_onsets(self,onsets,seconds):
        return np.subtract(onsets, seconds)

    def zero_any_negatives(self,onsets):
        onsets[onsets<0] = 0
        return onsets

    def create_new_folder(self,path):
        if not os.path.exists(path):
            os.makedirs(path)

    def folder_has_files(self,folder):
        try:
            for f in os.listdir(folder):
                if ".wav" in f:
                    return True
            else:
                return False
        except FileNotFoundError:
            return False

    def move_files_to_folder(self,folder_a,folder_b):
        pass
        #for f in os.listdir(folder_a):
        #    os.rename(folder_a + f, folder_b + f)

    def delete_files_in_folder(self,folder):
        files = glob.glob(folder)
        print(files)
        for f in files:
            os.remove(f)

    # NEEDS WORK
    def remove_close_onsets(self,onsets):
        new_onsets = []
        for i, onset in enumerate(onsets):
            if i==0:
                new_onsets.append(onset)
            elif onset-new_onsets[-1] < 0.3:
                pass
            else:
                new_onsets.append(onset)
        return new_onsets

    def delete_wav(self,filename):
        os.remove(filename)
#Slicer("/Users/richwhalley/Samples/sax.wav",[63,70],11)
# $ youtube-dl --extract-audio --audio-format wav -o [OUTPUT].wav '[URL]'
#Slicer("file.wav",[0,5],12)
#Slicer("/Users/richwhalley/Music/dinner.wav",[0,5],0)
#Slicer("/Users/richwhalley/Music/hailu.wav",[0,5],1)
#Slicer("/Users/richwhalley/Downloads/Pete Cannon SOS free sample pack/3 Drums And Breaks/amen heavy hitter.wav",[0,5],0)
