import os
import CONFIG as c


vl= '/Users/richwhalley/Documents/GitHub/quantum_sim/img/'


c1 = "/usr/local/bin/ffmpeg -r 18 -f image2 -s 1763x926 -i " +vl+"quantumspectral%04d.png -vf scale=1762:-2 -vcodec libx264 -crf 25  -pix_fmt yuv420p quantumbig.mp4"

cmds = [c1]

for c in cmds:
    os.system(c)
