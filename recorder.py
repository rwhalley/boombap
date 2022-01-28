from scipy.io.wavfile import read
# a = read("adios.wav")


import pyaudio
import wave
from slicer import Slicer
import time

class AudioRecorder():
    def __init__(self,seconds):

        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.DEV_INDEX = 0
        self.RATE = 44100
        self.CHUNK = 2048
        self.RECORD_SECONDS = seconds
        self.WAVE_OUTPUT_FILENAME = "file.wav"
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = None


    def start_record(self):
        # start Recording
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                        rate=self.RATE, input=True,
                        frames_per_buffer=self.CHUNK,
			input_device_index = self.DEV_INDEX)
        print ("recording...")
        self.frames = []

        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = self.stream.read(self.CHUNK, exception_on_overflow = False)
            self.frames.append(data)
        print ("finished recording")


    def stop_record(self):
        # stop Recording
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def create_wav(self):

        waveFile = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(self.CHANNELS)
        waveFile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        waveFile.setframerate(self.RATE)
        waveFile.writeframes(b''.join(self.frames))
        waveFile.close()


a= AudioRecorder(5)
a.start_record()
a.stop_record()
