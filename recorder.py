from scipy.io.wavfile import read
# a = read("adios.wav")


import pyaudio
import wave
import os
from slicer import Slicer
import time

class AudioRecorder():
    def __init__(self,seconds):

        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 4096#1024
        self.RECORD_SECONDS = seconds
        self.WAVE_OUTPUT_FILENAME = "file.wav"
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = None


    def start_record(self):
        # start Recording
        print("opening stream...")
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                        rate=self.RATE, input=True, input_device_index=1,
                        frames_per_buffer=self.CHUNK)
        print ("recording...")
        self.frames = []
        total = int(self.RATE / self.CHUNK * self.RECORD_SECONDS)
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)
            print(f"writing chunk {i} of {total}")
        print ("finished recording...")


    def stop_record(self):
        # stop Recording
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def create_wav(self):
        print("creating temporary wav file")
        waveFile = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(self.CHANNELS)
        waveFile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        waveFile.setframerate(self.RATE)
        waveFile.writeframes(b''.join(self.frames))
        waveFile.close()

    def delete_wav(self):
        print("deleting temporary wav file")
        os.remove(self.WAVE_OUTPUT_FILENAME)
