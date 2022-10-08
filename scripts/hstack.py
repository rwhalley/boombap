"""Stack videos vertically or horizontally"""

import os
import CONFIG as c

stack = 'hstack'  #'vstack'

vl= c.VIDEO_FINAL_OUTPUT_PATH + "piggo.mp4"
vr = c.VIDEO_FINAL_OUTPUT_PATH + "piggo2.mp4"
#vi = "../piggo.mp4" #video input filename
vo = c.VIDEO_FINAL_OUTPUT_PATH + "twopiggos2.mp4"
#vo = "pigggo.mp4" # video output filename

c1 = "ffmpeg -i "+vl+" -i "+vr+" -filter_complex "+stack+" " + vo

cmds = [c1]

for c in cmds:
    os.system(c)

