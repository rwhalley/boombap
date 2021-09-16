import rtmidi
import mido
import time
from threading import Thread, Lock


options = list(set(mido.get_input_names()))
print(options)

messages = []
threads = []

def parse_midi(lock):
    global messages
    lock.acquire()
    while True:
        if len(messages)>0:
            print(messages.pop(0))
    messages = []
    lock.release()


def midi_in(name, lock):
    global messages
    lock.acquire()
    with mido.open_input(name) as port:

        for i,message in enumerate(port):
            messages.append(message)
            #print(i)
            print(message)
    lock.release()



for device in options:
    threads.append(Thread(target=midi_in,args=(device,Lock())))
#t3 = Thread(target=parse_midi,args=(Lock(),))

#t3.start()
for thread in threads:
    thread.start()


for thread in threads:
    thread.join()

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
# for i in range(0,10):
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
