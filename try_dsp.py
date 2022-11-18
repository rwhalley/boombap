import numpy as np
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt


list = [1,2,3,4]
l=[]
l = l+list
l=l+list

print(l)

x = np.arange(0,10)
x = np.array([[1,1],[2,2],[3,3]])
print(x[:,1])
print(x.shape)

x = np.array([[3513, 3513],
        [2342, 2342],
              [2342, 2342],
              [2342, 2342],
              [2342, 2342],[2342, 2342],[2342, 2342],[2342, 2342],[2342, 2342],[2342, 2342],[2132, 2132]])

def stack_cols_from_list(l,ncols):
        output = []
        for i in range(ncols):
                output.append(l)
        output = np.array(output,dtype='int16').T
        return output

def normalize(x):
    return np.array(((x / np.max(np.abs(x))) * 32767),dtype='int16')

# ## --- LIMITER
# threshold = 0.8
# transfer = np.linspace(-32767, 32767, x.shape[0])
# transfer[transfer>(threshold*32767)] = int(threshold*32767)
# print(transfer.shape)
# #transfer = stack_cols_from_list(transfer,2)
# constant =  np.linspace(-32767, 32767, x.shape[0], dtype='int16')
# #transfer = constant**0.98
# #constant = stack_cols_from_list(constant,2)
# print(constant)
# print(transfer)

# --- COMPRESSOR

x = normalize(x)
factor = 1
constant =  np.linspace(-1, 1, x.shape[0])

transfer = np.arctan(factor * constant)

#print(transfer)
transfer /= np.abs(transfer).max()

transfer = normalize(transfer)
constant = normalize(constant)
#plt.plot(constant,transfer)
#plt.show()
print("TRANSFER")
print(transfer)

# factor: 1 is compressing some; 10 is a lot of compression
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
                print(i)
                col = input[:,i]
                f = interp1d(constant,transfer)
                output.append(f(col))

        output =  (np.array(output,dtype='int16').T)
        print(output)
        return output

print(x)
print(apply_compression(x))


#
#

# print(x[:,0])
#
# print(np.array([(x / np.max(np.abs(x))) * 32767], dtype='int16')[0])
#
#
# def apply_transfer(signal, transfer, interpolation='linear'):
#     constant = np.linspace(-32767, 32767, transfer.shape[0], dtype='int16')
#     print((transfer))
#     print((constant))
#     print((signal))
#     interpolator = interp1d(constant, transfer, interpolation)
#
#     return np.array(interpolator(signal ),dtype='int16')
#
# # hard limiting
# def limiter(x, treshold=1):
#     transfer_len = x.shape
#     transfer = np.linspace(-32767, 32767,transfer_len[0], dtype='int16')
#
#             #np.concatenate([ np.repeat(-1, int(((1-treshold)/2)*transfer_len)),
#             #                    np.linspace(-32767, 32767, int(treshold*transfer_len)),
#             #                    np.repeat(1, int(((1-treshold)/2)*transfer_len)) ])
#     print(f"transfer: {transfer}")
#
#     print(f"signal: {x}")
#     return apply_transfer(x, transfer)
#
# print(limiter(x[:,0])[0])
