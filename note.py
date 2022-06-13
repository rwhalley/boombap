class Note:
    def __init__(self,bar_position,midi,bank,port,when, loop_id,page):
        self.bar_position = bar_position
        self.midi = midi
        self.bank = bank
        self.page = page
        self.port = port
        self.when = when
        self.loop_id = loop_id  # id of loop that note is part of
