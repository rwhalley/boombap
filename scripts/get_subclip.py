# concatenate two movies
from moviepy.editor import *
import CONFIG as c

f1 = c.VIDEO_INPUT_PATH + "milk.MOV"# "../wendys2.mp4"
t0 = 0
t1 = 5

o = c.VIDEO_INPUT_PATH + "full.MOV" #"../superwendeees2.mp4"


c1 = VideoFileClip(f1).subclip(t0, t1)



c1.write_videofile(o,codec='libx264',
                                                                                                 audio_codec='aac',
                                                                                                 temp_audiofile='temp-audio.m4a',
                                                                                                 remove_temp=True)

#final.ipython_display(width = 480)
