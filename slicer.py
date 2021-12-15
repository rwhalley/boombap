import librosa
import numpy as np
import soundfile as sf

class Slicer:
    def __init__(self,input_wav_file, pre_slice,folder_num):
        self.input_wav, self.sample_rate = librosa.load(input_wav_file)
        print(self.input_wav)
        self.max_onsets = 16
        self.onsets = librosa.onset.onset_detect(y=self.input_wav, sr=self.sample_rate, units='samples',wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
        self.sliced =[ ]
        start_index = (self.sample_rate*pre_slice[0])
        end_index =(self.sample_rate*pre_slice[1])
        self.input_wav = self.input_wav[start_index:end_index]
        for i,onset in enumerate(self.onsets):
            if i==16:
                break
            else:
                print(onset)
                data =(self.input_wav[onset:self.onsets[i+1]])

                sf.write('./samples/'+str(folder_num)+'/'+str(i)+'.wav', data, self.sample_rate, subtype='PCM_16')



Slicer("/Users/richwhalley/Samples/sax.wav",[63,70],11)
