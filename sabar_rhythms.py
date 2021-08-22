from rhythm import Rhythm

kaolack = Rhythm()
kaolack.metronome = [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0]
kaolack.mbalax1 = [[1,0,0,0,0,1,0,0,1,0,0,0,0,2,0,0],  # pax
                   [0,0,0,1,0,0,0,0,0,0,0,1,1,0,0,0],  # gin
                   [0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1],  # tan
                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet
kaolack.talmbat = [[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],  # pax 4
                     [1,0,0,0,0,2,0,0,1,0,0,0,0,0,0,0],  # gin 0
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                     [0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],  # tan 2
                     [0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0]] # tet
kaolack.parts = [kaolack.mbalax1, kaolack.talmbat]

yaaba = Rhythm()
yaaba.metronome = [1,0,0,0,0,0,1,0,0,0,0,0,]
yaaba.mbalax1 = [[1,0,0,2,0,0,1,0,0,2,0,0],
                 [0,0,1,1,0,0,0,0,1,1,0,0],
                 [0,1,0,0,1,1,0,1,0,0,1,1],
                 [0,0,0,0,0,0,0,0,0,0,0,0]]
kaolack.talmbat =   [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax 4  EMPTY
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gin 0
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # tan 2
                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet
yaaba.parts = [yaaba.mbalax1,yaaba.talmbat]

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
thieboudjeun.parts = [thieboudjeun.mbalax1,thieboudjeun.talmbat]


empty = Rhythm()
empty.metronome =                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

empty.mbalax =                      [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gin
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # tan
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], # tet

empty.talmbat =                     [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax 4
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gin 0
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # tan 2
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] # tet 3
empty.parts = [empty.mbalax1,empty.talmbat]


rhythms = {"empty" : empty.parts, "kaolack" : kaolack.parts,"lumbuel":lumbuel.parts,'thieboudjeun':thieboudjeun.parts,"njouk":njouk.parts,"yaaba":yaaba.parts}
meters = {"empty":empty.metronome,"kaolack":kaolack.metronome,"lumbuel":lumbuel.metronome,'thieboudjeun':thieboudjeun.metronome,"njouk":njouk.metronome,"yaaba":yaaba.metronome}
button_order = ["empty","kaolack","lumbuel","thieboudjeun","njouk","yaaba"]
