import soundfile as sf
import pygame
import os
import time
import numpy
import wavio
import pickle



class SoundBank:
    def __init__(self):
        self.dir = './samples/'
        self.data = []
        self.current_sample_list = None
        self.sounds = []

    def file2np(self,filename):
        if 'DS_Store' in filename:
            pass
        else:

            self.data.append((pygame.sndarray.array(pygame.mixer.Sound(filename))))

    def get_sample_list(self):

        #self.current_sample_list = ([x[2] for x in walk(self.dir)])
        print(self.current_sample_list)
        file_set = set()

        for dir_, _, files in os.walk(self.dir):
            for file_name in files:
                rel_dir = os.path.relpath(dir_, self.dir)
                rel_file = os.path.join(rel_dir, file_name)
                file_set.add(rel_file)
        print(file_set)
        self.current_sample_list = file_set


    def preload_all_samples(self):
        for filename in self.current_sample_list:
            print(self.dir+filename)
            self.file2np(self.dir+filename)




sb = SoundBank()
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=32)
print(sb.get_sample_list())
t3 = time.time()
sb.preload_all_samples()
t4 = time.time()
print(sb.data)

sounds = []

pickle.dump(sb.data,open( "save.p", "wb" ))
t0 = time.time()
data = pickle.load(open( "save.p", "rb" ))

t1 = time.time()
for sound_arr in data:


    sound = pygame.sndarray.make_sound(sound_arr)
t2 = time.time()

print(t1-t0)
print(t2-t1)
print(t4-t3)
#path = './samples/0/0_pax_oh.wav'
#sound_arr = read(path)[1]
#print(sound_arr)
#time.sleep(1)
