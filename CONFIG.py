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
VIDEO_RECORDING_FOLDER = "04 - Video Recording"
VIDEO_INPUT_PATH = '/Volumes/SQUIRREL/Videos/Input/'
VIDEO_OUTPUT_PATH = '/Volumes/SQUIRREL/Simple/'+VIDEO_RECORDING_FOLDER+'/'
VIDEO_FINAL_OUTPUT_PATH = '/Volumes/SQUIRREL/Videos/FinalOutputs/'
VIDEO_TEMP_PATH = '/Volumes/SQUIRREL/Videos/Temp/'
AUDIO_FINAL_OUTPUT_PATH = '/Volumes/SQUIRREL/Videos/FinalOutputs/'
APPLY_START_OFFSET = False
START_OFFSET_F = -6 # frames
START_OFFSET_S = -0.25 #seconds
SLICE_LENGTH = 2.5  # length of video slices in seconds

#State
CURRENT_BANK = 0


# Preferences
BOOTUP_SOUND = 0
DEBUG_MODE = 1
DEBUG = False
DOUBLE = 1  # Double Length of Video Output
RECORDED_SAMPLES_FOLDER = "10 - Recorded"
VIDEO_RECORDING_FOLDER = "04 - Video Recording"

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
