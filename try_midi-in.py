import mido
from mido.ports import MultiPort
import time
from threading import Thread, Lock

def print_message(msg):
    print(msg)
options = list(set(mido.get_input_names()))
print(options)
mido.open_input(callback=print_message)

# for device in options:
#     if "Midi Through" in device:
#         pass
    #elif "reface CP" in device:
    #    mido.open_input(device, callback=print_message)

    # elif "QUNEO" in device:
    #     mido.open_input(device, callback=print_message)



while True:
    time.time()


messages = []
threads = []

# def parse_midi(lock):
#     global messages
#     #lock.acquire()
#     while len(messages)>0:
#         print(messages.pop(0))
#     messages = []
#     #lock.release()


#
#
# def midi_in(name):
#     global messages
#     #lock.acquire()
#     port = mido.open_input(name, callback=print_message)
#     while True:
#         port.callback = print_message
#     #lock.release()
#
#
#
#
# for device in options:
#     if "Midi Through" in device:
#         pass
#     else:
#         midi_in(device)
#         #threads.append(Thread(target=midi_in,args=(device,Lock())))
#
#
# for thread in threads:
#     thread.start()
#
# for thread in threads:
#     thread.join()

# ports = []
# for device in options:
#     if "Midi Through" in device:
#         pass
#     else:
#         ports.append(mido.open_input(device))
# multi = MultiPort(ports)
#
# for msg in multi:
#     print(msg)



#parse_midi()


# t1.join()
# t2.join()







# midiin.open_port(name='reface CP')
# while True:
#     messages = []
#     try:
#         messages.append(midiin.get_message())
#     except:
#         pass
#
#     for message in messages:
#         if message:
#             print(message)

#
# if available_ports:
#     midiout.open_port(0)
# else:
#     midiout.open_virtual_port("My virtual output")
#
# for i in range(0,8):
#     with midiout:
#         # channel 1, middle C, velocity 112
#         note_on = [0x90, 60, 112]
#         note_on2 = [0x90, 64, 112]
#         note_off = [0x90, 60, 0]
#         note_off2 = [0x90, 64, 0]
#         midiout.send_message(note_on)
#         midiout.send_message(note_on2)
#         time.sleep(0.2)
#         midiout.send_message(note_off)
#         midiout.send_message(note_off2)
#         time.sleep(0.5)
#
# del midiout
