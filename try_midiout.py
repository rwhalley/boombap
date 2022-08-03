import mido
import time
import CONFIG as c
import note_class

outport = None
light = True
if light:
    dev = c.MIDI_CONTROLLER
    devs = mido.get_output_names()
    print(devs)
    for d in devs:
        print(dev)
        print(d)
        if dev in d:
            print("Opening")
            outport = mido.open_output(d)
            break

for i in range(0,60):
    outport.send(note_class.Note(0,mido.Message('note_on', note=i),0,c.MIDI_CONTROLLER,time.time(), -2,0).midi)
    time.sleep(0.005)

for i in range(0,60):
    outport.send(note_class.Note(0,mido.Message('note_off', note=i),0,c.MIDI_CONTROLLER,time.time(), -2,0).midi)
    time.sleep(0.005)


# options = list(set(mido.get_input_names()))
# print(options)
#
# msg = mido.Message('note_on', note=44, velocity=100)
# msg_off = mido.Message('note_off', note=44, velocity=0)
# outport = mido.open_output('reface CP')
# outport.send(msg)
# outport.close()
# time.sleep(1)
# outport = mido.open_output('reface CP')
# outport.panic()
# outport.close()


# with mido.open_output('reface CP') as outport:
#     outport.send(msg)
