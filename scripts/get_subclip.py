# concatenate two movies
from moviepy.editor import *
import CONFIG as c

f1 = c.VIDEO_FINAL_OUTPUT_PATH + "robcoffeeeeee.mp4"# "../wendys2.mp4"
t0 = 8
t1 =32

o = c.VIDEO_INPUT_PATH + "robcoffeeeeeesh.mp4" #"../superwendeees2.mp4"


c1 = VideoFileClip(f1).subclip(t0, t1)



c1.write_videofile(o,codec='libx264',
                                                                                                 audio_codec='aac',
                                                                                                 temp_audiofile='temp-audio.m4a',
                                                                                                 remove_temp=True)

#final.ipython_display(width = 480)
