from drum import Drum

class Rhythm:

    def __init__(self):
        self.name = []
        self.drums = {
            "mbalax1": Drum("mbalax1"),
            "mbalax2": Drum("mbalax1"),
            "talmbat": Drum("talmbat"),
            "tulli": Drum("Tulli"),
            "tugone1": Drum("tugone1"),
            "tugone2": Drum("tugone2"),
            "kung1": Drum("Kung"),
            "kung2": Drum("Kung"),
            "nder": Drum("Nder")

        }
        self.mbalax1 = Drum("Mbung Mbung")
        self.mbalax2 = Drum("Mbung Mbung")
        self.talmbat = Drum("talmbat")
        self.tulli = Drum("Tulli")
        self.tugone1 = Drum("tugone1")
        self.tugone2 = Drum("tugone2")
        self.kung1 = Drum("Kung")
        self.kung2 = Drum("Kung")
        self.nder = Drum("N'Der")
        self.metronome = []
        self.parts = []
        self.notes_per_beat = None
        self.beats_per_bar = None
