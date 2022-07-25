OS = "m" #'m'


if OS == "r":
    PROGRAM_PATH = '/home/boombap/boombap/'
    USB = '/mnt/usb/Kits/'
    INPUT_DEVICE = 1
elif OS == 'm':
    PROGRAM_PATH = '/Users/richwhalley/Documents/GitHub/boombap/'
    USB = '/Volumes/SQUIRREL/Kits/'
    INPUT_DEVICE = 0


DEBUG_MODE = 1
RECORDED_SAMPLES_FOLDER = "10 - Recorded"


PORTS = {}

THREADING_ACTIVE = True
PI_FAST_LOAD = False

SYNTH_ONLY = 1



MIDI_CONTROLLER = 'QUNEO'
SYNTH = 'reface CP' #'minilogue KBD/KNOB'#"minilogue MIDI IN" #c.SYNTH
MY_DEVICES = [MIDI_CONTROLLER,SYNTH]
SYNTH_MIDI_CHANNEL = 0
MIDI_CONTROLLER_CHANNEL = 1

MAX_SABAR_BANK_INDEX = 3



# Constants

SEMITONE = .059#463094359
KEYBOARD_RANGE = 24


# OLD
# Program Config and Modes
ALL_SAMPLES = 0
ONE_BANK = 1

LOAD_SAMPLES = ONE_BANK
