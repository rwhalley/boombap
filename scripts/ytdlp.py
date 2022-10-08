# download a video from youtube for music video creation

import os

url = "https://www.youtube.com/watch?v=4NWO0DQ3LnA"
t0 = "05"
t1 = "25"

c1 = "yt-dlp -U" # update yt-dlp

c2 = "yt-dlp -S ext:mp4:m4a -o 'ttub.mp4' "+url # video 720p mp4 with m4a audio

c3 = "yt-dlp -f 'ba' -x --audio-format mp3 "+url # audio only

c4 = "ffmpeg  -ss 00:01:"+t0+ " -to 00:01:"+t1+"  -i ttub.mp4 -c copy teletub.mp4" # select specific time range


cmds = [c1,c2,c3,c4]

for c in cmds:
    os.system(c)

