import librosa
import numpy as np
import soundfile as sf
import os
import glob

class Slicer:
    def __init__(self,input_wav_file, pre_slice,folder_num):
        self.delete_files_in_folder('./samples/'+str(folder_num)+'/*')
        self.input_wav, self.sample_rate = librosa.load(input_wav_file)
        print(self.input_wav)
        self.max_onsets = 16
        self.onsets = librosa.onset.onset_detect(y=self.input_wav, sr=self.sample_rate, units='samples',wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
        self.sliced =[ ]
        self.onsets = self.zero_any_negatives(self.left_shift_onsets(self.remove_close_onsets(self.onsets),0.050))
        start_index = (self.sample_rate*pre_slice[0])
        end_index =(self.sample_rate*pre_slice[1])
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
                    sf.write('./samples/'+str(folder_num)+'/'+str(i)+'.wav', data, self.sample_rate, subtype='PCM_16')
        self.delete_wav(input_wav_file)

    def left_shift_onsets(self,onsets,seconds):
        return np.subtract(onsets,int(seconds*self.sample_rate))

    def zero_any_negatives(self,onsets):
        onsets[onsets<0] = 0
        return onsets

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

#Slicer("file.wav",[0,5],12)
