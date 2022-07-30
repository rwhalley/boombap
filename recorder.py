from scipy.io.wavfile import read
# a = read("adios.wav")


import pyaudio
import wave
import os
from slicer import Slicer
import time
import note_class
import mido
import CONFIG as c

class AudioRecorder():
    def __init__(self,seconds, controller=None):


        self.FORMAT = pyaudio.paInt16
        self.RATE = 44100
        self.CHUNK = 4096#1024
        self.RECORD_SECONDS = seconds
        self.WAVE_OUTPUT_FILENAME = "file.wav"
        self.audio = pyaudio.PyAudio()
        self.input_device_index = 1

        self.CHANNELS = 1
        print(self.audio.get_device_count())
        for i in range(self.audio.get_device_count()):
             dev = self.audio.get_device_info_by_index(i)
             name = dev['name']
             if name == c.MICROPHONE_NAME:
                self.CHANNELS = dev['maxInputChannels']
                self.input_device_index = i
        #     print(dev['maxInputChannels'])

        self.stream = None
        self.frames = None
        self.controller = controller


    def start_record(self):
        # start Recording
        print("opening stream...")
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                        rate=self.RATE, input=True, input_device_index=self.input_device_index,
                        frames_per_buffer=self.CHUNK)
        print ("recording...")
        self.controller.LED_out.play_note(note_class.Note(0, mido.Message('note_on', note=self.controller.button.RECORD_LED), 0, c.MIDI_CONTROLLER, time.time(), -2, 0), light=True)
        self.frames = []
        total = int(self.RATE / self.CHUNK * self.RECORD_SECONDS)
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)
            print(f"writing chunk {i} of {total}")
        print ("finished recording...")
        self.controller.LED_out.play_note(note_class.Note(0, mido.Message('note_off', note=self.controller.button.RECORD_LED), 0, c.MIDI_CONTROLLER, time.time(), -2, 0), light=True)



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
