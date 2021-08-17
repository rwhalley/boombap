kaolack = [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0]

kaolack_accompaniment =   [[[1,0,0,0,0,1,0,0,1,0,0,0,0,2,0,0],  # pax
                                 [0,0,0,1,0,0,0,0,0,0,0,1,1,0,0,0],  # gin
                                 [0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1],  # tan
                                 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], # tet

                                [[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],  # pax 4
                                 [1,0,0,0,0,2,0,0,1,0,0,0,0,0,0,0],  # gin 0
                                 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                 [0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],  # tan 2
                                 [0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0]]] # tet 3

lumbuel = [1,0,0,0,1,0,1,0,0,1,0,0]
lumbuel_accompaniment = [[[0,0,0,0,1,0,0,0,0,0,1,0],
                               [0,0,1,0,0,0,0,0,1,0,0,0],
                               [1,1,0,0,0,1,1,1,0,0,0,1],
                               [0,0,0,0,0,0,0,0,0,0,0,0]],

                              [[0,0,0,0,0,0,0,0,0,0,0,0],
                               [1,0,0,0,0,0,1,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,1,0,0,0,0,0,1],
                               [0,1,0,1,0,0,0,1,0,1,0,0]]]

njouk = kaolack  # Same Metronome
njouk_accompaniment = [[[0,0,2,0,0,0,0,0,0,0,2,0,0,0,1,0],  # pax
                             [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],  # gin
                             [0,0,0,1,1,0,1,0,0,0,0,1,1,0,1,0],  # tan
                             [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], # tet

                            [[0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0],  # pax 4
                             [1,0,0,1,0,0,0,0,1,0,0,1,0,0,0,0],  # gin 0
                             [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                             [0,0,1,0,1,0,0,1,0,0,1,0,1,0,0,1],  # tan 2
                             [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]] # tet 3

thieboudjeun = kaolack # Same Metronome
thieboudjeun_accompaniment =  [[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax
                                     [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],  # gin
                                     [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1],  # tan
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], # tet

                                    [[1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],  # pax 4
                                     [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],  # gin 0
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                     [0,0,1,0,0,1,0,0,0,0,1,0,0,1,0,0],  # tan 2
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]] # tet 3


empty                      =  [[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gin
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # tan
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], # tet

                                    [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # pax 4
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gin 0
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # ran 1
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # tan 2
                                     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]] # tet 3


rhythms = {"empty" : empty, "kaolack" : kaolack_accompaniment,"lumbuel":lumbuel_accompaniment,"thieboudjuen":thieboudjeun_accompaniment,"njouk":njouk_accompaniment}
meters = {"empty":kaolack,"kaolack":kaolack,"lumbuel":lumbuel,"thieboudjeun":thieboudjeun,"njouk":njouk}
button_order = ["empty","kaolack","lumbuel","thieboudjeun","njouk"]
