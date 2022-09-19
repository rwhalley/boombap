# #import onset_detect as od
# import datetime
# #filepath = '/Users/richwhalley/Music/kingtubby.wav'
# #print(od.get_onsets(filepath))
# # kits = [None] * 16
# #
# # kits[10] = 5
# #
# # print(kits)
# import time
# from timeit import default_timer
# from time import process_time
#
# t1 = time.time()
# counter = 0
# for i in range (1,100000):
#     time.time()
# t2 = time.time()
# print(t2-t1)

import skvideo.io
import skvideo.datasets
import numpy as np
import numpy.ma as ma
from skimage.transform import resize
from numba import jit, cuda
import math

# sine oscillating!!!!

bpm = 15
spm = 60
bps = bpm/spm
height = 400
width = 400
vpan = 450
hpan = 250
vpan2 = 925
hpan2 = 450
frames = 500
#videodata = skvideo.io.vread(skvideo.datasets.bigbuckbunny())
#videometadata = skvideo.io.ffprobe(skvideo.datasets.bigbuckbunny())


s = [(1,1.0),(2,2.0),(3,3.0)] # sequence
m = [1.0,1.5,2.0] # moments in the video


def  get_min(metadata, param):  # params = '@width', '@height', '@duration'
     min = 9999999999
     io = None
     for i,vmeta in enumerate(metadata):
          value = None
          print(vmeta)
          if param == '@duration':
               value = float(vmeta['video'][param])
          else:
               value = int(vmeta['video'][param])
          print(param)
          print(value)
          if value < min:
               min = value
               io = i
     return min

"""Extract clips from long video"""
def extract_clips(video,moments,durations=None,framerate=30):
     clips = []
     framepoints = moments*framerate
     num_moments = len(framepoints)
     for i,moment in enumerate(framepoints):
          if i == num_moments: # if last one, just end with end of video

               clip = video[framepoints[i]:len(video)]
          else:
               clip = video[framepoints[i]:framepoints[i+i]]
          clips.append(clip)
     return clips


"""Create Empty 3-channel Video of resolution x,y and length n frames"""
def create_empty_video(x,y,n):
     return  np.reshape(np.arange(x*y*n*3),(n,x,y,3))

"""Clip Zoom"""

"""Assemble videos based on time sequence"""
def assemble(videos,sequence,x=1080,y=1920,tframes=1,framerate=30):
     nv = create_empty_video(x,y,tframes) # New video of length total frames
     start = 0
     for event in sequence:
          vid = event[0]
          vt = event[1]
          nframes = len(videos[vid])
          if (start+nframes) < tframes:
               end = (start+nframes)
               end2 = (nframes)
          else:
               end = tframes
               end2 = (tframes-start)

          nv[start:end] = videos[vid][0:end2]
          start=int(framerate*vt)
     return nv


#@jit
def resize_video(vdata,vmeta,w,h): # resize all the images in  one video
     # for i in range(len(vdata)):
     #      print(w)
     #      print(h)
     #      vdata[i] = resize(vdata[i],(1920,1080),anti_aliasing=True)
     #
     hshift = 0
     wshift = 0
     h1=int(vmeta['video']['@height'])
     w1=int(vmeta['video']['@width'])
     if h1>h:
          hshift = int(abs((h1-h)/2))
     if w1>w:
          wshift = int(abs((w1-w)/2))


     vdata = vdata[:,wshift:w+wshift,hshift:h+hshift,:]

     return vdata

"""Mix videos of same length."""
def sin_mix_videos(v1,v2,f,mlen):  # video 1, video 2, frequency, length
     new = v1
     for i in range(mlen):
          freq = 2#bps*mlen
          mix = abs(math.cos(freq*(i/mlen)*2*math.pi))
          #mix = ((freq*i)%l)/l
          new[i] = mix*v1[i]+(1-mix)*v2[i]
     return new



def test_vid_assembly(vfilenames):
     #get metadata
     vmeta = get_metadata(vfilenames)


     # find min width, height, and length of all videos
     mw = get_min(vmeta,"@width")  # min width
     mh = get_min(vmeta,"@height")   # min height
     mlen = get_min(vmeta,"@nb_frames")  # min length

     # get raw data as 4D numpy arrays
     vdata = get_vdata(vfilenames)

     # resize data
     for i in range(len(vfilenames)):
          vdata[i] = resize_video(vdata[i],vmeta[i],mw,mh)

     output = assemble(vdata,s,x=mw,y=mh,tframes=mlen)
     skvideo.io.vwrite("sequence.mp4",output)


def preprocess_videos(vfilenames): # list of videos as input

     #get metadata
     vmeta = get_metadata(vfilenames)


     # find min width, height, and length of all videos
     mw = get_min(vmeta,"@width")  # min width
     mh = get_min(vmeta,"@height")   # min height
     mlen = get_min(vmeta,"@nb_frames")  # min length

     # get raw data as 4D numpy arrays
     vdata = get_vdata(vfilenames)

     print(vdata[2][:,:,:])
     #mask = ma.masked_equal(vdata[2][:,:,:], [0,0,0]).mask
     #mask = np.logical_not(mask)
     #print(mask)

     # resize data
     for i in range(len(vfilenames)):
          vdata[i] = resize_video(vdata[i],vmeta[i],mw,mh)

     # make all videos the same length of frames
     for i in range(len(vfilenames)):
          vdata[i] = vdata[i][0:mlen]

     # mix data
     print("Mixing First Video")
     new = sin_mix_videos(vdata[0],vdata[1],2,mlen)

     vdata[0] = None
     vdata[1] = None

     print("Mixing Second Video")
     new = sin_mix_videos(vdata[3],new,1.5,mlen)
     for i in range(mlen):
          freq = 1.5#bps*mlen
          mix = abs(math.cos(freq*(i/mlen)*2*math.pi))
          #mix = ((freq*i)%l)/l
          new[i] = mix*vdata[3][i]+(1-mix)*new[i]

     # get mask of dynamic data

     # mask = ma.masked_where(arr <= 0.5, arr).mask
     # print(arr)
     # print(mask)
     # print(np.where(mask,(arr*100 + arr*100),arr))


     # print(vdata[2][:][:])
     print("Getting mask")
     mask = np.logical_not(ma.masked_equal(vdata[2][:,:,:], [0,0,0]).mask)
     # print(mask)
     #
     print("Applying Floor Division")
     newt = new // 2

     print("Applying Floor Division 2")
     vdata[2] = vdata[2] // 2

     print("Applying mask")
     new = np.where(mask,(newt + vdata[2]),new)

     # new = np.putmask(vdata[2], mask, (0.5*new + vdata[2]*0.5))
     # print(vdata[2])
     # print(mask)

     #new = 0.5*new + 0.5*vdata[2]

     # write new video to disk
     print("Writing video to disk")
     skvideo.io.vwrite("allie.mp4",new)


def apply_mask(video,mask,greenscreenvalue = [0,0,0]):  # default greenscreen value is black 0,0,0
     output = video
     print("Getting mask")
     mask = np.logical_not(ma.masked_equal(video[2][:,:,:], [0,0,0]).mask)
     # print(mask)
     #
     print("Applying Floor Division")
     newt = output // 2

     print("Applying Floor Division 2")
     video[2] = video[2] // 2

     print("Applying mask")
     output = np.where(mask,(newt + video[2]),output)



def get_metadata(vfilenames):
     vmeta = []
     for i,fn in enumerate(vfilenames):
          vmeta.append(skvideo.io.ffprobe(fn))
     return vmeta

def get_vdata(vfilenames):
     vdata = []  # video data as numpy array
     for fn in vfilenames:
          vdata.append(skvideo.io.vread(fn))
     return vdata

vfilenames = ["goat.mov","chicken.mov","square.mp4", "allie.mov"]

test_vid_assembly(vfilenames)
#preprocess_videos(vfilenames)

# arr = np.random.random((3, 3))
# mask = ma.masked_where(arr <= 0.5, arr).mask
# print(arr)
# print(mask)
# print(np.where(mask,(arr*100 + arr*100),arr))


#
# vparams = ['@width', '@height', '@duration']
#
# vfilenames = ["goat.mov","chicken.mov"]
#
# vdata = []  # video data as numpy array
# for fn in vfilenames:
#      vdata.append(skvideo.io.vread(fn))
#
# vmeta = []  # length of each video in seconds
# for i,v in enumerate(vfilenames):
#      vmeta.append(skvideo.io.ffprobe(fn))
#
#
# videodata = skvideo.io.vread("goat.mov")
# videometadata = skvideo.io.ffprobe("goat.mov")
# print(videometadata)
# frame_rate = videometadata['video']['@avg_frame_rate']
#
# vd = skvideo.io.vread("chicken.mov")
#
#
#
# print(frame_rate[0:2])
# vlen = frames/int(frame_rate[0:2])
#
#
#
# vd = vd[0:frames,(0+vpan):(height+vpan),(0+hpan):(width+hpan),:]
# #videodata = videodata[0:frames]
# videodata = videodata[0:frames,(0+vpan2):(height+vpan2),(0+hpan2):(width+hpan2),:]
#
#
#
#
#
# new =  vd + videodata
# new = new
# print(len(videodata))
# l = len(videodata)
# for i in range(0,l):
#      freq = bps*vlen
#      mix = abs(math.cos(freq*(i/l)*2*math.pi))
#      #mix = ((freq*i)%l)/l
#      new[i] = mix*vd[i]+(1-mix)*videodata[i]
#
# skvideo.io.vwrite("new.mp4",new)
