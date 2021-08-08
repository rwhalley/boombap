class MIDIParse:
    @staticmethod
    def isNoteOn(msg):
        if msg[0][0] >=144 and msg[0][0] <= 159 and not MIDIParse.isNoteOff(msg):
            return True
        else:
            return False

    @staticmethod
    def getVelocity(msg):
        return msg([0][2])

    @staticmethod
    def getNoteNumber(msg):
        try:
            return msg[0][1]
        except:
            return msg[1]


    @staticmethod
    def isNoteOff(msg):
        if (msg[0][0] >=128 and msg[0][0] <= 143) or (msg[0][2] == 0):
            return True
        else:
            return False

    @staticmethod
    def isController(msg):
        if msg[0][0] >=176 and msg[0][0] <= 191:
            return True
        else:
            return False

    @staticmethod
    def getControllerValue(msg):
        return msg[0][2]

    @staticmethod
    def getTimeSinceLast(msg):
        return msg[1]
