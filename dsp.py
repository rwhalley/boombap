import numpy as np
from scipy.interpolate import interp1d
from scipy.io import wavfile

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
    #print(transfer)
    return apply_transfer(x, transfer)

# smooth compression: if factor is small, its near linear, the bigger it is the
# stronger the compression
def arctan_compressor(x, factor=10):
    constant = np.linspace(-1, 1, len(x))
    #print(constant)
    transfer = np.arctan(factor * constant)
    #print(transfer)
    transfer /= np.abs(transfer).max()
    #print(transfer)
    return apply_transfer(x, transfer*32767)
