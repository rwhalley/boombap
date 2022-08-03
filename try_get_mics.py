import pyaudio
import CONFIG as c
p = pyaudio.PyAudio()


print("INITIALIZING LED OUT")
print(c.MIDI_CONTROLLER)
print(c.POSSIBLE_MIDI_CONTROLLERS[0])
print(c.MIDI_CONTROLLER in c.POSSIBLE_MIDI_CONTROLLERS)
print(c.MIDI_CONTROLLER is 'QUNEO')
print(c.MIDI_CONTROLLER == 'QUNEO')


print(p.get_device_count())
for i in range(p.get_device_count()):
     dev = p.get_device_info_by_index(i)

     print(dev)
     name = dev['name']
     if c.MICROPHONE_NAME in name:
          print("MATCHY")

          print(dev['maxInputChannels'])
