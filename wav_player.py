import numpy
import wave
import pyaudio
from scipy.interpolate import interp1d

class WavPlayer:
    def __init__(self):

        self.wavs = []
        self.wavnames = []

        self.p = pyaudio.PyAudio()
        self.last_chunks = []
        self.last_chunk = None
        self.chunk_size = 2048
        self.framerate = 44100
        self.format = 8
        self.num_channels = 2
        self.stream = None
        self.silence = numpy.pad([], (0, self.chunk_size), 'constant').tobytes()


    def play(self,wav):
        self.wavnames.append(wav.filepath)
        self.wavs.append(wave.open(wav.filepath,'rb'))

    def stop(self,wav):
        try:
            i = self.wavnames.index(wav.filepath)
            self.wavs.pop(i)
        except IndexError:
            pass
        except ValueError:
            pass

    def open_stream(self):
            self.stream = self.p.open(format=self.format,
                            channels=self.num_channels,
                            rate=self.framerate,
                            output=True,
                            stream_callback=self.multicallback)

            self.stream.start_stream()



    def close(self):

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def multicallback(self,in_data,frame_count,time_info,status):

        if self.wavs:
            datas = []
            for i,wav in enumerate(self.wavs):
                datas.append(numpy.fromstring(wav.readframes(frame_count),numpy.int16))


                if (datas[i].size < self.chunk_size):
                    if (datas[i].size == 0):
                        self.wavs.pop(i)
                    else:
                        diff = self.chunk_size - datas[i].size
                        datas[i] = numpy.pad(datas[i], (0, diff), 'constant')
            data = sum(datas)
            #print(data)
            #data = self.arctan_compressor(data)
            return (data.tobytes(), pyaudio.paContinue)

        else: # Run silence to keep stream going
            return (self.silence,pyaudio.paContinue)


    def arctan_compressor(self,x, factor=5):
        constant = numpy.linspace(-1, 1, len(x))
        #print(constant)
        transfer = numpy.arctan(factor * constant)
        #print(transfer)
        transfer /= numpy.abs(transfer).max()
        #print(transfer)
        return self.apply_transfer(x, transfer*32767)

    def apply_transfer(self,signal, transfer, interpolation='linear'):
        constant = numpy.linspace(-32767, 32767, len(transfer))
        #print((transfer))
        #print((constant))
        #print((signal))
        interpolator = interp1d(constant, transfer, interpolation, fill_value="extrapolate")
        return interpolator(signal)
