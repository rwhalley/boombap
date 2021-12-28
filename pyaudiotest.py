import pyaudio
import wave
import time
import sys
import numpy
from scipy.interpolate import interp1d
from samplerate import resample
from scipy import signal
from threading import Thread


class WavPlayer:
    def __init__(self):
        self.wf = wave.open('./samples/6/rim.wav', 'rb')
        #self.wf_2 = wave.open('./samples/6/mid tom.wav', 'rb')
        self.wavs = []
        self.wavnames = []
        #self.data = []
        # instantiate PyAudio (1)
        self.p = pyaudio.PyAudio()
        self.last_chunks = []
        self.last_chunk = None
        self.chunk_size = 1024
        self.stream = None


    def play(self,filepath):
        self.wavnames.append(filepath)
        self.wavs.append(wave.open(filepath,'rb'))

    def stop(self,filepath):
        try:
            i = self.wavnames.index(filepath)
            self.wavs.pop(i)
        except IndexError:
            pass



    def multicallback(self,in_data,frame_count,time_info,status):

        if self.wavs:
            datas = []
            for i,wav in enumerate(self.wavs):
                datas.append(numpy.fromstring(wav.readframes(frame_count),numpy.int16))
                if (datas[i].size == 0):
                    self.wavs.pop(i)
                if (datas[i].size < self.chunk_size):
                    diff = self.chunk_size - datas[i].size
                    datas[i] = numpy.pad(datas[i], (0, diff), 'constant')
            data = sum(datas)
            return (data.tobytes(), pyaudio.paContinue)

        else:
            return (numpy.pad([], (0, self.chunk_size), 'constant').tobytes(),pyaudio.paContinue)

    # define callback (2)
    def callback(self,in_data, frame_count, time_info, status):
        data1 = self.wf.readframes(frame_count)
        data2 = self.wf_2.readframes(frame_count)
        decodeddata1 = numpy.fromstring(data1, numpy.int16)
        decodeddata2 = numpy.fromstring(data2, numpy.int16)
        #print(int(decodeddata1.size))

        # if no frames left in wav 1, just make data = wav 2
        if(int(decodeddata1.size)==0):
            newdata = (decodeddata2).astype(numpy.int16)
            return (newdata.tostring(), pyaudio.paContinue)

        # if no frames left in wav 2, just make data = wav 1
        if(int(decodeddata2.size)==0):
            newdata = (decodeddata1).astype(numpy.int16)
            return (newdata.tostring(), pyaudio.paContinue)

        #  if size of frames is less than 1024 (framesize) append zeros to end of frames
        if(int(decodeddata1.size)>int(decodeddata2.size)):
            rest = int(decodeddata1.size)-int(decodeddata2.size)
            for i in range(1,rest+1):
                decodeddata2 = numpy.append(decodeddata2,0)

        if(int(decodeddata1.size)<int(decodeddata2.size)):
            rest = int(decodeddata2.size)-int(decodeddata1.size)
            for i in range(1,rest+1):
                decodeddata1 = numpy.append(decodeddata1,0)


        newdata = (decodeddata1 + decodeddata2).astype(numpy.int16)
        #newdata = (newdata*1).astype("int16")
        newdata = self.arctan_compressor(newdata).astype("int16")
        #newdata = resample(newdata,1.0,'sinc_best').astype("int16")
        #newdata = signal.resample(newdata,512).astype("int16")

        newdata = self.lowpass_filter(newdata).astype("int16")
        print(newdata)
        # if self.last_chunks:
        #     print("chunky")
        #     for chunk in self.last_chunks:
        #         newdata = ((newdata + (chunk*0.1))*0.8).astype('int16')
        #
        # self.last_chunk = newdata
        # if len(self.last_chunks)<20:
        #     self.last_chunks.append(self.last_chunk)
        # else:
        #     self.last_chunks.insert(0,self.last_chunk)
        #     self.last_chunks.pop()

        return (newdata.tostring(), pyaudio.paContinue)


    def lowpass_filter(self,data):
        N=5
        Wn=0.1
        B,A = signal.butter(N,Wn,output='ba')
        return signal.filtfilt(B,A,data)

    def open_stream(self):
        # open stream using callback (3)
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                        channels=self.wf.getnchannels(),
                        rate=self.wf.getframerate(),
                        output=True,
                        stream_callback=self.multicallback)

        # start the stream (4)
        self.stream.start_stream()
                # wait for stream to finish (5)



    def close(self):

        # stop stream (6)
        self.stream.stop_stream()
        self.stream.close()

        self.wf.close()
        #self.wf_2.close()

        # close PyAudio (7)
        self.p.terminate()

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


ts = time.time()
w = WavPlayer()


#w.play('./samples/8/04.wav')
#w.play('./samples/8/02.wav')


w.open_stream()

w.play('./samples/8/01.wav')

not_played = True
not_stopped = True

while w.stream.is_active():
    #time.sleep(0.1)
    if time.time()-ts > 1 and not_stopped:
        w.stop('./samples/8/01.wav')
        not_stopped = False
    if time.time()-ts > 0.5 and not_played:
        print("YES")
        w.play('./samples/8/04.wav')
        not_played = False


w.close()

print("WOW")




