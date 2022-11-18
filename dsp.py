import numpy as np
from scipy.interpolate import interp1d
from scipy.io import wavfile
from threading import Thread
import CONFIG as c





def apply_transfer(signal, transfer, interpolation='linear'):
    constant = np.linspace(-32767, 32767, len(transfer))
    #print((transfer))
    #print((constant))
    #print((signal))
    interpolator = interp1d(constant, transfer, interpolation, fill_value="extrapolate")
    return interpolator(signal)

# hard limiting
def limiter(x, treshold=1):
    transfer_len = len(x)
    transfer = np.concatenate([ np.repeat(-1, int(((1-treshold)/2)*transfer_len)),
                                np.linspace(-32767, 32767, int(treshold*transfer_len)),
                                np.repeat(1, int(((1-treshold)/2)*transfer_len)) ])
    #print(f"transfer: {transfer}")
    #print(f"signal: {x}")
    return apply_transfer(x, transfer)

# smooth compression: if factor is small, its near linear, the bigger it is the
# stronger the compression
def arctan_compressor(x, factor=5):
    constant = np.linspace(-1, 1, len(x))
    #print(constant)
    transfer = np.arctan(factor * constant)
    #print(transfer)
    transfer /= np.abs(transfer).max()
    #print(transfer)
    return apply_transfer(x, transfer*32767)


def normalize(x):
    return np.array(((x / np.max(np.abs(x))) * 32767),dtype='int16')


def apply_compression(input, factor=1):
    input = normalize(input)
    constant =  np.linspace(-1, 1, input.shape[0])
    transfer = np.arctan(factor * constant)
    transfer /= np.abs(transfer).max()
    transfer = normalize(transfer)
    constant = normalize(constant)

    return apply_interp(input,constant,transfer)



def apply_interp(input,constant,transfer):

        output=[]
        for i in range(input.shape[1]):
                #print(i)
                col = input[:,i]
                f = interp1d(constant,transfer)
                output.append(f(col))

        output =  (np.array(output,dtype='int16').T)
        #print(output)
        return output
