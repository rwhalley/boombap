from rhythm import Rhythm

kaolack = Rhythm()
kaolack.metronome = [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0]
kaolack.drums["mbalax1"].pax = [1,0,0,0,0,1,0,0,1,0,0,0,0,2,0,0]  # pax
kaolack.drums["mbalax1"].gin = [0,0,0,1,0,0,0,0,0,0,0,1,1,0,0,0]  # gin
kaolack.drums["mbalax1"].tan = [0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1]  # tan
kaolack.drums["mbalax1"].tet = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] # tet
kaolack.drums["mbalax1"].load_drum()

kaolack.drums["talmbat"].pax = [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0]  # pax 4
kaolack.drums["talmbat"].gin = [1,0,0,0,0,2,0,0,1,0,0,0,0,0,0,0]  # gin 0
kaolack.drums["talmbat"].rwan = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]  # ran 1
kaolack.drums["talmbat"].tan = [0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1]  # tan 2
kaolack.drums["talmbat"].tet = [0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0] # tet
kaolack.drums["talmbat"].load_drum()


kaolack.parts = [kaolack.mbalax1, kaolack.talmbat]
kaolack.notes_per_beat = 4
kaolack.beats_per_bar = 4

yaaba = Rhythm()
yaaba.metronome = [1,0,0,0,0,0,1,0,0,0,0,0,]
yaaba.mbalax1 = [[1,0,0,2,0,0,1,0,0,2,0,0],
                 [0,0,1,1,0,0,0,0,1,1,0,0],
                 [0,1,0,0,1,1,0,1,0,0,1,1],
                 [0,0,0,0,0,0,0,0,0,0,0,0]]
kaolack.talmbat =   [[0,0,0,0,0,0,0,0,0,0,0,0],  # pax 4  EMPTY
                     [0,0,0,0,0,0,0,0,0,0,0,0],  # gin 0
                     [0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                     [0,0,0,0,0,0,0,0,0,0,0,0],  # tan 2
                     [0,0,0,0,0,0,0,0,0,0,0,0]] # tet
yaaba.parts = [yaaba.mbalax1,yaaba.talmbat]
yaaba.notes_per_beat = 3
yaaba.beats_per_bar = 4

lumbuel = Rhythm()
lumbuel.metronome = [1,0,0,0,1,0,1,0,0,1,0,0]
lumbuel.mbalax1 =             [[0,0,0,0,1,0,0,0,0,0,1,0],
                               [0,0,1,0,0,0,0,0,1,0,0,0],
                               [1,1,0,0,0,1,1,1,0,0,0,1],
                               [0,0,0,0,0,0,0,0,0,0,0,0]]

lumbuel.talmbat =             [[0,0,0,0,0,0,0,0,0,0,0,0],
                               [1,0,0,0,0,0,1,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,1,0,0,0,0,0,1],
                               [0,1,0,1,0,0,0,1,0,1,0,0]]
lumbuel.parts = [lumbuel.mbalax1,lumbuel.talmbat]
lumbuel.notes_per_beat = 3
lumbuel.beats_per_bar = 4

njouk = Rhythm()
njouk.metronome = [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0]
njouk.mbalax1 =             [[0,0,2,0,0,0,0,0,0,0,2,0,0,0,1,0],  # pax
                             [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],  # gin
                             [0,0,0,1,1,0,1,0,0,0,0,1,1,0,1,0],  # tan
                             [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet

njouk.talmbat =             [[0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0],  # pax 4
                             [1,0,0,1,0,0,0,0,1,0,0,1,0,0,0,0],  # gin 0
                             [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                             [0,0,1,0,1,0,0,1,0,0,1,0,1,0,0,1],  # tan 2
                             [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet 3
njouk.parts = [njouk.mbalax1,njouk.talmbat]
njouk.notes_per_beat = 4
njouk.beats_per_bar = 4


thieboudjeun = Rhythm()
thieboudjeun.metronome = [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0]
thieboudjeun.mbalax1 =  [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax
                                     [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],  # gin
                                     [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1],  # tan
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet

thieboudjeun.talmbat =              [[1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],  # pax 4
                                     [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],  # gin 0
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                     [0,0,1,0,0,1,0,0,0,0,1,0,0,1,0,0],  # tan 2
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]  # tet 3

thieboudjeun.tulli =                [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax 4
                                     [0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0],  # gin 0
                                     [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                     [0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0],  # tan 2
                                     [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0]]  # tet 3

thieboudjeun.tugone1 =              [[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],  # pax
                                     [1,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0],  # gin
                                     [0,0,0,0,0,0,0,0,1,0,1,0,0,1,0,0],  # tan
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet

thieboudjeun.tugone2 =              [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax
                                     [0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0],  # gin
                                     [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],  # tan
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet
thieboudjeun.parts = [thieboudjeun.mbalax1,thieboudjeun.talmbat]
thieboudjeun.notes_per_beat = 4
thieboudjeun.beats_per_bar = 4

#
# fass = Rhythm()
# fass.metronome = [1,0,0,0,0,0,1,0,0,0,0,0]
# fass.mbalax1 =        [[0,0,0,0,0,0,0,0,0,0,0,0], #pax
#                        [0,1,0,0,1,0,0,1,0,0,1,0], #gin
#                        [1,0,1,1,0,1,1,0,1,1,0,1], #tan
#                        [0,0,0,0,0,0,0,0,0,0,0,0]] #tet
#
# fass.talmbat =        [[0,0,0,0,0,0,0,0,0,0,0,0], #pax
#                        [1,0,0,0,0,0,1,0,0,0,0,0], #gin
#                        [0,0,0,1,0,0,0,0,0,1,0,0], #ran
#                        [0,1,0,0,0,1,0,1,0,0,0,1], #tan
#                        [0,0,0,0,0,0,0,1,0,1,0,0]] #tet

niari_gorong = Rhythm()
niari_gorong.metronome = [1,0,0,0,0,0,1,0,0,0,0,0]
niari_gorong.mbalax1 =        [[0,0,0,0,0,0,0,0,0,0,0,0], #pax
                               [0,1,0,0,1,0,0,1,0,0,1,0], #gin
                               [1,0,1,1,0,1,1,0,1,1,0,1], #tan
                               [0,0,0,0,0,0,0,0,0,0,0,0]] #tet
niari_gorong.talmbat =        [[0,0,0,0,0,0,0,0,0,0,0,0], #pax
                               [1,0,0,0,0,0,1,0,0,0,0,0], #gin
                               [0,0,0,1,0,0,0,0,0,1,0,0], #ran
                               [0,1,0,0,0,1,0,1,0,0,0,1], #tan
                               [0,0,0,0,0,0,0,1,0,1,0,0]] #tet
niari_gorong.tugone1 =        [[0,0,0,0,0,0,0,0,0,0,0,0], #pax
                               [1,1,1,0,0,0,1,1,1,0,0,0], #gin
                               [0,0,0,0,0,0,0,0,0,0,0,0], #tan
                               [0,0,0,2,1,1,0,0,0,2,1,1]] #tet
niari_gorong.parts = [niari_gorong.mbalax1,niari_gorong.talmbat]
niari_gorong.notes_per_beat = 3
niari_gorong.beats_per_bar = 4


empty = Rhythm()
empty.metronome =                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

empty.mbalax =                      [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gin
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # tan
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet

empty.talmbat =                     [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax 4
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gin 0
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # tan 2
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet 3
empty.parts = [empty.mbalax1,empty.talmbat]
empty.notes_per_beat = None
empty.beats_per_bar = None


met22 = Rhythm()
met22.metronome =                    [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0]

met22.mbalax =                      [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gin
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # tan
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet

met22.talmbat =                     [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax 4
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gin 0
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # tan 2
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet 3
met22.parts = [met22.mbalax1,met22.talmbat]
met22.notes_per_beat = 4
met22.beats_per_bar = 4

met44 = Rhythm()
met44.metronome =                    [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0]

met44.mbalax =                      [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gin
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # tan
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet

met44.talmbat =                     [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax 4
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gin 0
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # tan 2
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet 3
met44.parts = [met44.mbalax1,met44.talmbat]
met44.notes_per_beat = 4
met44.beats_per_bar = 4


met34 = Rhythm()
met34.metronome =                    [1,0,0,0,1,0,1,0,0,1,0,0]

met34.mbalax =                      [[0,0,0,0,0,0,0,0,0,0,0,0],  # pax
                                     [0,0,0,0,0,0,0,0,0,0,0,0],  # gin
                                     [0,0,0,0,0,0,0,0,0,0,0,0],  # tan
                                     [0,0,0,0,0,0,0,0,0,0,0,0]] # tet

met34.talmbat =                     [[0,0,0,0,0,0,0,0,0,0,0,0],  # pax 4
                                     [0,0,0,0,0,0,0,0,0,0,0,0],  # gin 0
                                     [0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                     [0,0,0,0,0,0,0,0,0,0,0,0],  # tan 2
                                     [0,0,0,0,0,0,0,0,0,0,0,0]] # tet 3
met34.parts = [met34.mbalax1,met34.talmbat]
met34.notes_per_beat = 3
met34.beats_per_bar = 4

barembaye = Rhythm()
ardin = Rhythm()
walowalo = Rhythm()



rhythms = {"empty" : empty.parts,"met22" : met22.parts,"met44" : met44.parts,"met34" : met34.parts, "kaolack" : kaolack.drums,"lumbuel":lumbuel.parts,'thieboudjeun':thieboudjeun.parts,"njouk":njouk.parts,"yaaba":yaaba.parts,"niari_gorong":niari_gorong.parts}
meters = {"empty":empty.metronome,"met22" : met22.metronome,"met44" : met44.metronome,"met34" : met34.metronome,"kaolack":kaolack.metronome,"lumbuel":lumbuel.metronome,'thieboudjeun':thieboudjeun.metronome,"njouk":njouk.metronome,"yaaba":yaaba.metronome,"niari_gorong":niari_gorong.metronome}
button_order = ["empty","met22","met44","met34","kaolack","lumbuel","thieboudjeun","njouk","yaaba","niari_gorong"]
objects = [empty,met22,met44,met34,kaolack,lumbuel,thieboudjeun,njouk,yaaba,niari_gorong]
