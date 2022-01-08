class Drum:
    def __init__(self, name):
        self.name = name
        self.drum = None
        self.gin = None
        self.pin = None
        self.pax = None
        self.tan = None
        self.tet = None
        self.rwan = None
        self.drin = None
        #self.cek = None
        self.cex = None

    def load_drum(self):
        self.drum = {
            "gin" : self.gin,
            "pin" : self.pin,
            "pax" : self.pax,
            "tan" : self.tan,
            "tet" : self.tet,
            "rwan" : self.rwan,
            "drin" : self.drin,
            #"cek" : self.cek,
            "cex" : self.cex
        }
