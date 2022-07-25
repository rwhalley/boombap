
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
RECORD_LED = 34

# Left Triangle Shift Buttons
BANK_SELECTOR = 11  # Select Drum Kit on Pads - Row 1 Left
PAGE_SELECTOR = 12  # Select Bank of Drums on Pads - Row 1 Right
METRONOME = 13  # Select Metronome on Pads - Row 2 Left
LOOP_ACTIVATOR_SHIFT = 14  # Activate and Deactivate Loops on Pads - Row 1 Right
TRACK_SAVE_SHIFT = 15
TRACK_LOAD_SHIFT = 16
REVERB = 17  # While pressed, other pressed notes will get reverb
SHIFT_4R = 18 # Not Used

VOLUME_SHIFT = 10



MODE_SHIFT = 26

#Mode nums - hold down MODE_SHIFT and press pads 1-16
RELOAD_ALL_SOUND_DATA = 0  # Not Yet Implemented
SWITCH_LOOP_LENGTH = 1
AUDIO_RECORD_MODE_NUM = 2 # pad 2
VELOCITY_SENSITIVITY = 3 # 25 pad 3
MUTE_METRONOME = 4
SAVE_STATE = 5 # Example: Saves all volumes


PADS = range(PAD_START,PAD_START+16)
SHIFT_BUTTONS = [BANK_SELECTOR,METRONOME,TRACK_LOAD_SHIFT, TRACK_SAVE_SHIFT, MODE_SHIFT,PAGE_SELECTOR,LOOP_ACTIVATOR_SHIFT,REVERB]
SWITCH_BUTTONS = [PITCH_UP,PITCH_DOWN,BPM_UP,BPM_DOWN,RECORD,EXIT,CLEAR_LOOP]




