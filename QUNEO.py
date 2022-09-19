
BANK_UP = -100
BANK_DOWN = -100
EXIT = 24
VOL_UP = 4444444
VOL_DOWN = 555555
CLEAR_LOOP = 19
RECORD = 25  # 18

BPM_CONTROL = 6
BPM_UP = 20
BPM_DOWN = 21
MBUNG_VOL_CONTROL = 0
COL_VOL_CONTROL = 1
PITCH_CONTROL = 10
PITCH_UP = 22
PITCH_DOWN = 23
PAD_START = 52

# LEDS
METRONOME_LED = 38
RECORD_LED = 34
ON_LED = 35
KEYBOARD_LED = 43

# Left Triangle Shift Buttons
BANK_SELECTOR = 11  # Select Drum Kit on Pads - Row 1 Left
PAGE_SELECTOR = 12  # Select Bank of Drums on Pads - Row 1 Right
METRONOME = 13  # Select Metronome on Pads - Row 2 Left
LOOP_ACTIVATOR_SHIFT = 14  # Activate and Deactivate Loops on Pads - Row 1 Right
TRACK_SAVE_SHIFT = 15 # also used for  cut group
TRACK_LOAD_SHIFT = 16
REVERB = 17  # While pressed, other pressed notes will get reverb
KEYBOARD = 18 #

VOLUME_SHIFT = 10



MODE_SHIFT = 26

#Mode nums - hold down MODE_SHIFT and press pads 1-16
RELOAD_ALL_SOUND_DATA = 0
SWITCH_LOOP_LENGTH = 1
SAVE_STATE = 2  # Example: Saves all volumes # Reexport all pickle files - can save keyboards
VELOCITY_SENSITIVITY = 3

MUTE_METRONOME = 4
AUDIO_RECORD_MODE_NUM = 5
AUDIO_RECORD_MODE_NUM_SHARP = 6
AUDIO_RECORD_NO_SLICE = 7

SAVE_PAGE = 8 # save positions and settings on  current page - not yet implemented
VIDEO_SEQ = 9 # Send Items recorded on video page to "My_Loop" to Video Sequencer
AUDIO_EXPORT = 10 # Export current loop to audio
VIDEO_SLICER = 11 # Slice a video and send it to sample banks


VIDEO_PAGE = 15 # Last Page is video page


PADS = range(PAD_START,PAD_START+16)
SHIFT_BUTTONS = [BANK_SELECTOR,METRONOME,TRACK_LOAD_SHIFT, TRACK_SAVE_SHIFT, MODE_SHIFT,PAGE_SELECTOR,LOOP_ACTIVATOR_SHIFT,REVERB]
SWITCH_BUTTONS = [PITCH_UP,PITCH_DOWN,BPM_UP,BPM_DOWN,RECORD,EXIT,CLEAR_LOOP, KEYBOARD]




