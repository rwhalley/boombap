path = '/Volumes/SQUIRREL/Kits'
import os
from os import listdir, walk
from os.path import isfile, join, exists
from soundy_pygame import Soundy

from dataclasses import dataclass

@dataclass
class Sample:
    name: str
    path: str

@dataclass
class Kit:
    name: str
    path: str
    samples: list

@dataclass
class Page:
    name: str
    path: str
    kits: list


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def get_all_kit_dirs(path):
    output = []
    for dir in sorted(get_immediate_subdirectories(path)):
        output.append(sorted(get_immediate_subdirectories(path+'/'+dir+'/')))
    return output

pages = (sorted(get_immediate_subdirectories(path)))
kits_names = get_all_kit_dirs(path)
print(kits_names)

all_sounds = []
for i, page in enumerate(pages):
    kits = []
    for kit_name in kits_names[i]:
        kit = Kit(kit_name,path+'/'+page+'/'+kit_name+'/',[])
        samples = [f for f in sorted(listdir(kit.path)) if isfile(join(kit.path, f))]
        for file in samples:
            if file.endswith('.wav'):
                if file.startswith('.'):
                    pass
                else:
                    kit.samples.append(Soundy(kit.path+file))

        kits.append(kit)

    all_sounds.append(Page(page,path+'/'+page+'/',kits))

print(all_sounds)


#
# def load_all_samples(self):
#         print("# Loading All Samples from File")
#         self.all_sounds = []
#         if c.PI_FAST_LOAD:
#             max = 1
#         else:
#             max = 32
#         for i in range(0,max): #  Load first 32 banks only
#             try:
#                 bank = []
#                 path = self.basepath + str(i)+'/'
#                 onlyfiles = [f for f in sorted(listdir(path)) if isfile(join(path, f))]
#                 for file in onlyfiles:
#                     if file.endswith('.wav'):
#                         if file.startswith('.'):
#                             pass
#                         else:
#                             bank.append(Soundy(path+file))
#                 self.all_sounds[self.current_page].append(bank)
#             except FileNotFoundError:
#                 #print("less than 8 sample banks found")
#                 pass
#         for bank in self.all_sounds:
#             if c.PI_FAST_LOAD:
#                 print("PI FAST LOAD ACTIVE")
#             else:
#                 self.pre_process_sounds(sounds = bank)
#
