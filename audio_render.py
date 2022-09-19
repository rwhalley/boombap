"""Class for rendering audio output from sequenced wav files"""
import numpy as np
import QUNEO as c
from scipy.io.wavfile import write
import dsp


class AudioRender:

     def __init__(self):
          self.bar_length = 4
          self.bpm = 120
          self.bpl = 4  #bars per loop
          self.spm = 60  # seconds per minute
          self.input = []
          self.all_sounds = None
          self.loop = None
          self.loop_length_seconds = ((self.bar_length)/self.bpm)*self.spm*self.bpl
          self.sample_rate = 44100 # frames per second
          self.last_output_filename = None




     """Mix two sound signals of same frame length together"""
     def mix_sounds(self,s1,s2):
          s1 = s1//2
          s2 = s2//2
          return dsp.normalize(s1+s2)

     """Create Empty 2-channel Audio numpy with 16-bit depth and length n frames"""
     def create_empty_audio(self,n):
          return np.zeros((n,2),dtype='int16')
          #return  np.reshape(np.arange(n*2,dtype='int32'),(n,2))

     """Export output audio loop to WAV"""
     def export_audio(self,arr,filename,loop,bpm):
          self.bpm = bpm
          self.loop = loop
          self.all_sounds = arr
          self.loop_length_seconds =  ((self.bar_length)/self.bpm)*self.spm*self.bpl

          # Create an empty audio frame that is the length of the desired recording
          self.output = self.create_empty_audio(int(self.sample_rate*self.loop_length_seconds))


          # Load the loop data
          # Retrieve all the sounds that are in loop data
          # at each time point in  loop, mix in the sounds
          print("Rendering Audio Output from Sample Loop...")
          for entry in self.loop:
               if entry.midi.type == "note_on":

                    # Retrieve the sample wav data
                    note = (entry.midi.note - c.PAD_START)
                    page = entry.page
                    kit = entry.bank
                    print(f"note: {note}")
                    print(f"kit: {kit}")
                    print(f"page: {page}")
                    sound = self.all_sounds[page].kits[kit].samples[note].get_original_sound_array()
                    samplelen = len(sound)


                    # Calculate the start and end index for output
                    ts = ((entry.bar_position * self.bar_length)/self.bpm)*self.spm*self.bpl  ## 1.34 measures * 4 beats per measure * / 120 beats per minute * 60 seconds per minute bpm 120 / 4 beats   ((1.34 * 4)/120)*60 = seconds
                    start= int(ts*self.sample_rate)
                    end = int(start+samplelen)




                    #find "note_off" index and update end index if note off's before sample's done
                    for entry in self.loop:
                         if entry.midi.type == "note_off":
                              if entry.page == page and entry.bank == kit and (entry.midi.note - c.PAD_START) == note:
                                   ts = ((entry.bar_position * self.bar_length)/self.bpm)*self.spm*self.bpl  ## 1.34 measures * 4 beats per measure * / 120 beats per minute * 60 seconds per minute bpm 120 / 4 beats   ((1.34 * 4)/120)*60 = seconds
                                   note_off = int(ts*self.sample_rate)
                                   if (note_off < end) and (note_off > start):
                                        end = note_off


                    print(f"start: {start}")
                    print(f"end: {end}")


                    if end> len(self.output):
                         end = len(self.output)

                    # Mix in the wav sample into the appropriate indices of output
                    self.output[start:end] = self.mix_sounds(self.output[start:end],sound[:(end-start)])

                    print(entry.bar_position)
                    print(ts)

          # Export Audio to File
          print(f"Exporting audio to wav: {filename}")
          self.last_output_filename = filename
          print(self.output)
          # double length of audio
          self.output = np.concatenate((self.output,self.output), axis=0)

          write(filename, self.sample_rate, self.output)




