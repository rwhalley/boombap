import slicer
from os import path
from pydub import AudioSegment
import numpy as np

mp3 = "/Users/richwhalley/Music/hailu.mp3"
wav = "hailu.wav"



# files
src = "transcript.mp3"
dst = "test.wav"

# convert wav to mp3
sound = np.array(AudioSegment.from_mp3(mp3).get_array_of_samples())
print(sound)

#sound.export(dst, format="wav")
