import mido
import time

options = list(set(mido.get_input_names()))
print(options)

msg = mido.Message('note_on', note=44, velocity=100)
msg_off = mido.Message('note_off', note=44, velocity=0)
outport = mido.open_output('reface CP')
outport.send(msg)
outport.close()
time.sleep(1)
outport = mido.open_output('reface CP')
outport.panic()
outport.close()


# with mido.open_output('reface CP') as outport:
#     outport.send(msg)
