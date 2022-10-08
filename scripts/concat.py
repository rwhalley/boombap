# concatenate two movies
from moviepy.editor import *
import CONFIG as c

f1 = c.VIDEO_FINAL_OUTPUT_PATH + "teletubby.mp4"# "../wendys2.mp4"
t0 = 0
t1 = 5

f2 = c.VIDEO_FINAL_OUTPUT_PATH + "weirdteletoub.mp4" #"../wendys3.mp4"
t3 = 0
t4 = 10

o = c.VIDEO_FINAL_OUTPUT_PATH + "teletubz.mp4" #"../superwendeees2.mp4"


c1 = VideoFileClip(f1)#.subclip(t0, t1)
c2 = VideoFileClip(f2)#.subclip(t3,t4)

final = concatenate_videoclips([c1, c2])
final.write_videofile(o,codec='libx264',
                                                                                                 audio_codec='aac',
                                                                                                 temp_audiofile='temp-audio.m4a',
                                                                                                 remove_temp=True)

#final.ipython_display(width = 480)

