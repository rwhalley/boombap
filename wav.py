import wave

class Wav:
    def __init__(self,filepath):
        self.filepath = filepath
        print(self.filepath)
        self.data = wave.open(self.filepath,'rb')
        self.pitch = 0 # In Semitones
        self.pad = 0  # pad index
        self.volume = 127  # 0-127

    def set_volume(self,vol):
        if vol >= 127:
            self.volume = 127
        if vol < 0:
            self.volume = 0
        self.volume = vol


