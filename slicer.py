import librosa
import numpy as np
import soundfile as sf

class Slicer:
    def __init__(self,input_wav_file):
        self.input_wav, self.sample_rate = librosa.load(input_wav_file)
        print(self.input_wav)
        self.max_onsets = 16
        self.onsets = librosa.onset.onset_detect(y=self.input_wav, sr=self.sample_rate, units='samples')
        self.sliced =[ ]
        for i,onset in enumerate(self.onsets):
            if i==16:
                break
            else:
                print(onset)
                data =(self.input_wav[onset:self.onsets[i+1]])
                sf.write('./samples/4/test'+str(i)+'.wav', data, self.sample_rate, subtype='PCM_16')



Slicer("./samples/2/  - Marker #19.wav")
