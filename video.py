"""Autogenerate video from MIDI/Sound input"""
import os
import skvideo.io
import skvideo.datasets

import numpy as np
import numpy.ma as ma
from skimage.transform import resize
from numba import jit, cuda
import math
import moviepy.editor as mp

import QUNEO as q
import CONFIG as c

# sine oscillating!!!!


class Video:

    def __init__(self):

        # bpm = 15
        # spm = 60
        # bps = bpm/spm
        # height = 400
        # width = 400
        # vpan = 450
        # hpan = 250
        # vpan2 = 925
        # hpan2 = 450
        # frames = 500
        #videodata = skvideo.io.vread(skvideo.datasets.bigbuckbunny())
        #videometadata = skvideo.io.ffprobe(skvideo.datasets.bigbuckbunny())
        self.audiopath = None
        self.videopath = None
        self.outputpath = None
        self.framerate_str = None
        self.framerate = 30
        self.w = 1080
        self.h = 1920
        self.dimensions = str(self.w)+"x"+ str(self.h)
        self.loop_cancellist = []

        self.s = [(1,0.5,0),(2,1.5,1),(3,2.5,1)] # sequence
        self.m = [0.0,1.0] # moments in the video
        self.exported_videos = []  # List of filenames that are exported in a session

    """Convert int video width and height to ffmpeg string format"""
    def get_dimen(self,w,h):
        return str(w)+"x"+ str(h)

    """Get minimum metadata value. For example - width height and duration..."""
    def  get_min(self,metadata, param):  # params = '@width', '@height', '@duration'
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
    def extract_clips(self,video,moments,durations=None,framerate=30):
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
    def create_empty_video(self,x,y,n):
        return  np.zeros((n,x,y,3),dtype='int16')
         #return  np.reshape(np.arange(x*y*n*3),(n,x,y,3))

    """Clip Zoom"""

    """Assemble video clips based on timestamps with associated clip IDs. 
    This is where the output video actually gets assembled."""
    def assemble(self,videos,sequence,x=None,y=None,tframes=1,framerate=30, vdimen = None, vindex = None, vbanks = None):
         self.dimensions = vdimen

         # Make room for the assembled video to repeat twice
         if c.DOUBLE:
             tframes = tframes*2


         # Create an empty numpy array to hold the video data with the correct length
         nv = self.create_empty_video(x,y,tframes) #+int(framerate)) # New video of length total frames
         print(self.dimensions)
         print(f"NEW VIDEO SHAPE: {nv.shape}")


         #Iterate through the MIDI loop events
         start = 0
         for event in sequence:

              vid = event[0] # What number PAD was pressed
              vt = event[1]  # what is the timepoint of the event in seconds
              vbank = event[2]
              start=int(framerate*vt)
              if start<0:
                  start = 0

              print(f"Assembling  Event: {str(vid)}, {str(vt)}")
              nframes = int(c.SLICE_LENGTH*framerate)#len(videos[vid])
              if (start+nframes) < tframes:
                   end = (start+nframes)
                   end2 = (nframes)
              else:
                   end = tframes
                   end2 = (tframes-start)

              # print("START")
              # print(vid)
              # print(len(nv))
              # print(len(videos))
              #
              # print(start)
              # print(end)
              # print(end2)
              print(f"VIDEOSHAPE {len(videos)}")
              print(f"VINDEX {vindex}")
              result = 0
              i=0
              while vbanks[i]<vbank:
                  result += (vindex[i]) + 1  # 1 is added for each 0 index
                  i+=1
              result = result + vid
              # for ind in vindex:
              #     if ind[0] == vid and ind[2] == vbank:
              #         result = ind[2]
              print(f"result: {result}")

              myvid = videos[result]
              print(f"MYVID + {myvid}")
              if len(videos[result])<end2:
                  while len(videos[result])<end2:
                      videos[result] = np.concatenate((videos[result],videos[result]), axis=0  )
              nv[start:end] = videos[result][0:end2]
              # print(f"VIDEO shape: {myvid.shape}")
              # print(f"VIDEO: {vid}")
              # print(myvid[0:end2])
              #videos[vid] = 0

         #print(f"NEW VIDEO: {nv}")
         if c.DOUBLE:
             # double the video output
             nv[int(len(nv)/2):(len(nv))] = nv[0:int(len(nv)/2)]
             return nv[0:len(nv)]
         else:
             return nv


    #@jit
    """Resize the video by cropping"""
    def resize_video(self,vdata,w,h, hshift=0,wshift=0): # resize all the images in  one video
         # for i in range(len(vdata)):
         #      print(w)
         #      print(h)
         #      vdata[i] = resize(vdata[i],(1920,1080),anti_aliasing=True)
         #

         h1=vdata.shape[2]#int(vmeta['video']['@height'])
         w1=vdata.shape[1]#int(vmeta['video']['@width'])
         if h1>h:
              hshift = int(abs((h1-h)/2))
         if w1>w:
              wshift = int(abs((w1-w)/2))


         vdata = vdata[:,wshift:w+wshift,hshift:h+hshift,:]

         return vdata

    """Mix videos of same length."""
    def sin_mix_videos(self,v1,v2,f,mlen):  # video 1, video 2, frequency, length
         new = v1
         for i in range(mlen):
              freq = 2#bps*mlen
              mix = abs(math.cos(freq*(i/mlen)*2*math.pi))
              #mix = ((freq*i)%l)/l
              new[i] = mix*v1[i]+(1-mix)*v2[i]
         return new





    def preprocess_videos(self,vfilenames): # list of videos as input

         #get metadata
         vmeta = self.get_metadata(vfilenames)


         # find min width, height, and length of all videos
         # mw = self.get_min(vmeta,"@width")  # min width
         # mh = self.get_min(vmeta,"@height")   # min height
         # mlen = self.get_min(vmeta,"@nb_frames")  # min length

         # get raw data as 4D numpy arrays
         vdata = self.get_vdata(vfilenames)

         mw = min([v.shape[1] for v in vdata])
         mh = min([v.shape[2] for v in vdata])
         mlen = min([v.shape[0] for v in vdata])

         self.dimensions = self.get_dimen(mw,mh)
         self.w = mw
         self.h = mh

         print(vdata[2][:,:,:])
         #mask = ma.masked_equal(vdata[2][:,:,:], [0,0,0]).mask
         #mask = np.logical_not(mask)
         #print(mask)

         # resize data
         for i in range(len(vfilenames)):
              vdata[i] = self.resize_video(vdata[i],mw,mh)

         # make all videos the same length of frames
         for i in range(len(vfilenames)):
              vdata[i] = vdata[i][0:mlen]

         # mix data
         print("Mixing First Video")
         new = self.sin_mix_videos(vdata[0],vdata[1],2,mlen)

         vdata[0] = None
         vdata[1] = None

         print("Mixing Second Video")
         new = self.sin_mix_videos(vdata[3],new,1.5,mlen)
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

    def pad_video(self,input,n,w,h, x=0, y=0):
        mn,mx,my = input.shape[0], input.shape[1], input.shape[2]
        output = self.create_empty_video(w,h,n)
        output[:,x:w+x,y:h+y,:] = input
        return output

    """Overlays a 'mask' video onto an input video, excluding the greenscreen color"""
    def apply_mask(self,input,mask,greenscreenvalue = [0,0,0]):  # default greenscreen value is black 0,0,0
         output = input

         mn,mx,my = mask.shape[0], mask.shape[1], mask.shape[2]
         inn,inx,iny = input.shape[0], input.shape[1], input.shape[2]

         # make mask same size as input video
         if mx<inx and my<iny:
             mask = self.pad_video(mask,inn,inx,iny)

         print("Getting mask")
         mask = np.logical_not(ma.masked_equal(mask[:,:,:], greenscreenvalue).mask)
         # print(mask)

         print("Applying Floor Division")
         newt = output // 2

         print("Applying Floor Division 2")
         input = input // 2

         print("Applying mask")
         return(np.where(mask,(newt + input),output))




    """Export the video clip with associated audio data."""
    def export_video_with_audio(self,audiopath):
        print(self.videopath)
        print(audiopath)
        print("trying.mp4")
        filename = input()
        self.exported_videos.append(filename)
        mp.VideoFileClip(self.videopath).set_audio(mp.AudioFileClip(audiopath)).write_videofile(c.VIDEO_FINAL_OUTPUT_PATH+filename,
                                                                                                codec='libx264',
                                                                                                 audio_codec='aac',
                                                                                                 temp_audiofile='temp-audio.m4a',
                                                                                                 remove_temp=True)

    """String the videos together exported videos """
    def concatenate_videos(self):
        if (len(self.exported_videos) == 2):
            for i in range((len(self.exported_videos)-1)):

                f1 = c.VIDEO_FINAL_OUTPUT_PATH + self.exported_videos[i]# "../wendys2.mp4"

                f2 = c.VIDEO_FINAL_OUTPUT_PATH + self.exported_videos[i+1] #"../wendys3.mp4"
                t3 = 0
                t4 = 10
                fn_out = os.path.splitext(self.exported_videos[i])[0]+"o" + ".mp4"


                o = c.VIDEO_FINAL_OUTPUT_PATH + fn_out #"../superwendeees2.mp4"


                c1 = mp.VideoFileClip(f1)#.subclip(t0, t1)
                c2 = mp.VideoFileClip(f2)#.subclip(t3,t4)

                final = mp.concatenate_videoclips([c1, c2])

                final.write_videofile(o,codec='libx264',
                                         audio_codec='aac',
                                         temp_audiofile='temp-audio.m4a',
                                         remove_temp=True)
                try:
                    for video in self.exported_videos:
                        os.remove(c.VIDEO_FINAL_OUTPUT_PATH + video)
                except FileNotFoundError:
                    print("FILE NOT FOUND")
                self.exported_videos = list()
                self.exported_videos.append(fn_out)

    """Get video metadata for a list of video filenames. 
    Needed for figuring out compatible lengths and sizes for video processing."""
    def get_metadata(self,vfilenames):
         vmeta = []

         for i,fn in enumerate(vfilenames):
              vmeta.append(skvideo.io.ffprobe(fn))
         vmeta.append(vfilenames)
         return vmeta

    """Get the raw video data for a list of filenames. This is the raw data for preprocessing."""
    def get_vdata(self,vfilenames):
         vdata = []  # video data as numpy array

         for fn in vfilenames:
              output = skvideo.io.vread((fn), inputdict={'-r' : str(int(self.framerate))})
              vdata.append(output)
              #print(f"vdata output: {output}")

         return vdata

    """Delete any video data stored in memory in case it takes up all the RAM."""
    def cleanup(self):
        del self.voutputs
        self.voutputs = None
        del self.vdata
        self.vdata = None
        del self.adata
        self.adata = None
        del self.aoutputs
        self.aoutputs = None


    """Main function for assembling a musical video sequence from a MIDI loop. MIDI loop is parsed for video entries.
    Timestamps and video clip IDs are compiled and sent to a function where the actual video data is assembled into an output. """
    def assemble_sequence(self, loop, bpm, bar_length = 4, default_vid = 0, vname= "testoutput.mp4", all_sounds = None, vdimen=None, framerate=None, framerate_str=None, on_loops=None):

          self.framerate_str = framerate_str


          #["goat.mov","chicken.mov"]#,"square.mp4", "allie.mov"]



          print("Creating Video Sequence")
         # Create Video Sequence from MIDI Loop
          spm = 60  # seconds per minute
          input = []
          banks = []
          vindex = []
          #input.append((default_vid,0.0))\


          for entry in loop:
               if entry.loop_id in on_loops and entry.loop_id not in self.loop_cancellist:
                   # If the clip is to be automatically generated, i.e. sample has associated video
                   #if all_sounds[entry.page].kits[entry.bank].samples[entry.midi.note - q.PAD_START].has_video and entry.midi.type == "note_on":  # if the sample has a video clip
                   vbank = entry.bank
                   if not vbank in banks:
                       banks.append(vbank)
                   if entry.midi.type == "note_on" and entry.page == c.VIDEO_PAGE:  # if the sample has a video clip

                       vid = (entry.midi.note - q.PAD_START)
                       if c.APPLY_START_OFFSET:
                           offset= c.START_OFFSET_S
                       else: offset = 0
                       vt = ((entry.bar_position * bar_length)/bpm)*spm*4 + offset# + c.VIDEO_START_OFFSET_SECONDS  ## 1.34 measures * 4 beats per measure * / 120 beats per minute * 60 seconds per minute bpm 120 / 4 beats   ((1.34 * 4)/120)*60 = seconds
                       print(entry.bar_position)
                       print(vt)
                       input.append((vid,vt,vbank))

                   # If the video clip is manually sequenced from the video page (VIDEO ONLY, NO ASSOCIATED AUDIO)
                   elif entry.page == q.VIDEO_PAGE and entry.midi.type == "note_on":  # if the videos are hand sequenced in page 15
                        vid = (entry.midi.note - q.PAD_START)
                        vt = ((entry.bar_position * bar_length)/bpm)*spm*4  ## 1.34 measures * 4 beats per measure * / 120 beats per minute * 60 seconds per minute bpm 120 / 4 beats   ((1.34 * 4)/120)*60 = seconds
                        print(entry.bar_position)
                        print(vt)
                        input.append((vid,vt,vbank))

          self.loop_cancellist += on_loops  # add current on loops to cancel list
          print(input)

          # Locate video filenames in video folder
          print("Retrieving filenames")
          vfilenames = []
          folder_sizes = []
          starti = 0
          print(banks)
          banks.sort()
          for bank in banks:
                vfilenamestemp = [(c.VIDEO_OUTPUT_PATH+f"{bank:02d}"+"/"+f) for f in os.listdir(c.VIDEO_OUTPUT_PATH+f"{bank:02d}"+"/") if (not f.startswith('.'))  and (f.endswith('.MOV') or f.endswith('.mp4'))]
                tempi = 0
                for i, f in enumerate(vfilenamestemp):
                    vindex.append((i,i+starti,bank))
                    tempi = i
                folder_sizes.append(tempi)
                starti = starti + tempi
                vfilenames.append(vfilenamestemp)
          vfilenames = [item for sublist in vfilenames for item in sublist]
          print(f"vfilenames {vfilenames}")

          print("Retrieving Metadata")

          self.vmeta = self.get_metadata(vfilenames)

          # get frame rate from metadata or from function input
          self.framerate = framerate# (float(self.vmeta['@nb_frames'])/float(self.vmeta['@duration']))


          # make videos same dimensions
         # find min width, height, and length of all videos
          #mw = self.get_min(vmeta,"@width")  # min width
          #mh = self.get_min(vmeta,"@height")   # min height
          #mlen = self.get_min(vmeta,"@nb_frames")  # min length



          print("Loading Raw Data")
         # get raw data as 4D numpy arrays
          vdata = self.get_vdata(vfilenames)


          mw = min([v.shape[1] for v in vdata])
          mh = min([v.shape[2] for v in vdata])
          mlen = min([v.shape[0] for v in vdata])
          #
          mlen = int(((bar_length)/bpm)*spm*4 * self.framerate)
          print(f"MLEN: {mlen}")


          self.dimensions = self.get_dimen(mw,mh)
          self.w = mw
          self.h = mh


          print("Resizing Raw Data")
         # resize data
          #for i in range(len(vfilenames)):
          #     vdata[i] = self.resize_video(vdata[i],vmeta[i],mw,mh)

          #
          print("Assembling Video Data")
          print(input)
          new = self.assemble(vdata,input,x=self.w,y=self.h,tframes=mlen,framerate=self.framerate, vdimen=self.dimensions, vindex=folder_sizes, vbanks = banks)
          #print(f"NEW {new}")

          """fill in the empty frames at the beginning of the video with the first non-empty frame"""
          new = self.adjust_start_of_video(new)

          print("Writing video to disk")
          self.videopath = vname
          self.outputpath = vname

          skvideo.io.vwrite(vname,new, inputdict={'-r' : self.framerate_str})#str(int(self.framerate))})#, outputdict={'-s' : self.dimensions})

    """Fill in the first blank frames of the video with the first frame that contains data"""
    def adjust_start_of_video(self, video):
        i=0
        while i<len(video):
            if video[i].any():  # when you hit the first frame that isn't all 0's
                for j in range(0,i):
                    video[j] = video[i]
                break
            i+=1
        return video

    def test_vfilenames(self):
        banks = [0,1]
        vfilenames = []
        starti = 0
        vindex = []
        folder_sizes = []
        for bank in banks:
            vfilenamestemp = [(c.VIDEO_OUTPUT_PATH+f"{bank:02d}"+"/"+f) for f in os.listdir(c.VIDEO_OUTPUT_PATH+f"{bank:02d}"+"/") if (not f.startswith('.'))  and (f.endswith('.MOV') or f.endswith('.mp4'))]
            tempi = 0
            for i, f in enumerate(vfilenamestemp):
                vindex.append((i,i+starti,bank))
                tempi = i
            folder_sizes.append(tempi)
            starti = starti + tempi
            vfilenames.append(vfilenamestemp)
        vfilenames = [item for sublist in vfilenames for item in sublist]
        print(f"vfilenames {vfilenames}")
        return vfilenames,folder_sizes

    def test_vid_assembly(self,vfilenames,folder_sizes):
         #get metadata
         vmeta = self.get_metadata(vfilenames)
         # get raw data as 4D numpy arrays
         vdata = self.get_vdata(vfilenames)
         print(vdata)
         print(vmeta)


         # find min width, height, and length of all videos
         # mw = self.get_min(vmeta,"@width")  # min width
         # mh = self.get_min(vmeta,"@height")   # min height
         # mlen = self.get_min(vmeta,"@nb_frames")  # min length


         mw = min([v.shape[1] for v in vdata])
         mh = min([v.shape[2] for v in vdata])
         mlen = min([v.shape[0] for v in vdata])

         #mlen = int(((bar_length)/bpm)*spm*4 * self.framerate)
         print(f"MLEN: {mlen}")



         # resize data
         # for i in range(len(vfilenames)):
         #      vdata[i] = self.resize_video(vdata[i],mw,mh)
         #
         output = self.assemble(vdata,self.s,x=mw,y=mh,tframes=mlen,vindex=folder_sizes)
         output = self.adjust_start_of_video(output)
         skvideo.io.vwrite("sequence.mp4",output)


# vfilenames = ["goat.mov","chicken.mov", "allie.mov"]
#
# v = Video()
# output = v.test_vfilenames()
# v.test_vid_assembly(output[0],output[1])