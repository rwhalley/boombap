"""Downsample a video for easier file sharing"""

import os
import CONFIG as c

vi= c.VIDEO_INPUT_PATH + "kayak.mp4"
#vi = "../piggo.mp4" #video input filename
vo = c.VIDEO_INPUT_PATH + "kayak_sm.mp4"
#vo = "pigggo.mp4" # video output filename
width = 480 # keep aspect ratio

c1 = 'ffmpeg -y -i "'+vi+'" -vf scale='+str(width)+':-2,setsar=1:1 -c:v libx264 -c:a copy "'+vo+'"' #




cmds = [c1]

for c in cmds:
    os.system(c)

