import time
import rtmidi





for i in range(0,10):
    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()

    if available_ports:
        midiout.open_port(1)
    else:
        midiout.open_virtual_port("My virtual output")
    with midiout:
        time.sleep(0.4)
        # channel 1, middle C, velocity 112
        note_on = [0x90, 60, 112]
        note_on2 = [0x90, 64, 112]
        note_off = [0x90, 60, 0]
        note_off2 = [0x90, 64, 0]
        midiout.send_message(note_on)
        midiout.send_message(note_on2)
        time.sleep(0.2)
        midiout.send_message(note_off)
        midiout.send_message(note_off2)
        time.sleep(0.5)

    del midiout
