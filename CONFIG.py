OS = 'm'#"r" #



MICROPHONE_NAME = None

if OS == "r":
    PROGRAM_PATH = '/home/boombap/boombap/'
    USB = '/mnt/usb/Kits/'
    ARCHIVE = '/mnt/usb/ArchivedSamples/'
    INPUT_DEVICE = 1
    MICROPHONE_NAME = 'USB PnP Sound Device'
elif OS == 'm':
    PROGRAM_PATH = '/Users/richwhalley/Documents/GitHub/boombap/'
    USB = '/Volumes/SQUIRREL/Kits/'
    ARCHIVE = '/Volumes/SQUIRREL/ArchivedSamples/'
    INPUT_DEVICE = 0
    MICROPHONE_NAME = 'MacBook Pro Microphone'


"""VIDEO SETTINGS"""
VIDEO_INPUT_PATH = '/Volumes/SQUIRREL/Videos/Input/'
VIDEO_OUTPUT_PATH = '/Volumes/SQUIRREL/Videos/Output/'
VIDEO_FINAL_OUTPUT_PATH = '/Volumes/SQUIRREL/Videos/FinalOutputs/'
VIDEO_TEMP_PATH = '/Volumes/SQUIRREL/Videos/Temp/'
VIDEO_START_OFFSET_SECONDS = -0.5
SLICE_LENGTH = 2.5  # length of video slices in seconds


DEBUG_MODE = 1
DEBUG = False
RECORDED_SAMPLES_FOLDER = "10 - Recorded"

SIMPLE_MODE = True

if SIMPLE_MODE:
    RECORDED_SAMPLES_FOLDER = "03 - Recorded"
    if OS == "r":
        USB = '/mnt/usb/Simple/'
    if OS == "m":
        USB = '/Volumes/SQUIRREL/Simple/'





PORTS = {}

THREADING_ACTIVE = True
PI_FAST_LOAD = False

SYNTH_ONLY = 1

QUNEO = 'QUNEO'

MIDI_CONTROLLER = QUNEO
POSSIBLE_MIDI_CONTROLLERS = [QUNEO]
SYNTH = 'reface CP' #'minilogue KBD/KNOB'#"minilogue MIDI IN" #c.SYNTH

MY_DEVICES = [MIDI_CONTROLLER,SYNTH]
SYNTH_MIDI_CHANNEL = 0
MIDI_CONTROLLER_CHANNEL = 1

MAX_SABAR_BANK_INDEX = 3



# Constants

SEMITONE = .059#463094359
BPM_CHANGE_FACTOR = 0.05
KEYBOARD_RANGE = 24
NUM_PADS = 16  # the number of pads on the midi controller


# OLD
# Program Config and Modes
ALL_SAMPLES = 0
ONE_BANK = 1

LOAD_SAMPLES = ONE_BANK
