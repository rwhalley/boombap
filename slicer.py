#from librosa import load
#from librosa.onset import onset_detect

import numpy as np
import soundfile as sf
import os
import glob
from datetime import datetime as dt

class Slicer:
    def __init__(self,input_wav_file, pre_slice,folder_num):
        self.path = './samples/'+str(folder_num)+'/'
        self.old_files_path = './oldsamples/' + str(dt.now().strftime("%y%m%d%H%M%S"))+"/"
        self.input_wav_file = input_wav_file
        self.pre_slice = pre_slice
        if int(folder_num)>7:
            self.slice_samples()
        #self.delete_files_in_folder('./samples/'+str(folder_num)+'/*')




    def slice_samples(self):
        if not self.folder_has_files(self.path):  # If there
            self.create_new_folder(self.path)
        else:
            self.create_new_folder(self.old_files_path)
            self.move_files_to_folder(self.path,self.old_files_path)

        self.input_wav, self.sample_rate = None, None #load(self.input_wav_file)
        print(self.input_wav)
        self.max_onsets = 16
        self.onsets = [] #onset_detect(y=self.input_wav, sr=self.sample_rate, units='samples',wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
        self.sliced =[ ]
        self.onsets = self.zero_any_negatives(self.left_shift_onsets(self.remove_close_onsets(self.onsets),0.050))
        start_index = (self.sample_rate*self.pre_slice[0])
        end_index =(self.sample_rate*self.pre_slice[1])
        self.input_wav = self.input_wav[start_index:end_index]
        for i,onset in enumerate(self.onsets):
            if i==16:
                break
            else:
                print(onset)
                data = None
                if i< (len(self.onsets)-1):
                    data =(self.input_wav[onset:self.onsets[i+1]])

                elif i == (len(self.onsets)-1):
                     data = self.input_wav[onset:(len(self.input_wav)-1)]
                if hasattr(data, 'shape'):
                    sf.write(self.path+str(i)+'.wav', data, self.sample_rate, subtype='PCM_16')
        self.delete_wav(self.input_wav_file)

    def left_shift_onsets(self,onsets,seconds):
        return np.subtract(onsets,int(seconds*self.sample_rate))

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
        for f in os.listdir(folder_a):
            os.rename(folder_a + f, folder_b + f)

    def delete_files_in_folder(self,folder):
        files = glob.glob(folder)
        print(files)
        for f in files:
            os.remove(f)

    def remove_close_onsets(self,onsets):
        for i,onset in enumerate(onsets):
            if i< (len(onsets)-1) and ((onsets[i+1]-onsets[i]) < int(self.sample_rate/5)):
                print(onset)
                onsets = np.delete(onsets,i+1)
        return onsets

    def delete_wav(self,filename):
        os.remove(filename)
#Slicer("/Users/richwhalley/Samples/sax.wav",[63,70],11)
# $ youtube-dl --extract-audio --audio-format wav -o [OUTPUT].wav '[URL]'
#Slicer("file.wav",[0,5],12)
