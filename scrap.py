from operator import itemgetter

dict = {}
brick = {}

dict[1] = "father"
brick[5] = "bricks"

print(dict)
print(dict[1])
dict[5] = brick[5]

print(dict)

dict.pop(5)

print(dict)


play_loops = {0: [[0.12175, ([144, 37, 61], 0.07840698900000001), 0, 'QUNEO', 1631566936.736512], [0.08925, ([144, 37, 19], 2.835676222), 0, 'QUNEO', 1631566936.60726],[0.586, ([144, 37, 24], 1.738047914), 0, 'QUNEO', 1631566938.5935512], [0.6265, ([144, 37, 82], 0.106296942), 0, 'QUNEO', 1631566938.756171], [0.43075, ([144, 0, 127], 3.118313122), 0, 'QUNEO', 1631566941.973238], [0.62275, ([144, 1, 127], 0.46656720100000004), 0, 'QUNEO', 1631566942.7412748], [0.983, ([144, 25, 127], 1.080998343), 0, 'QUNEO', 1631566944.1817229]]}




# for key in play_loops:
#     for note in play_loops[key]:
#
#         print(f"play loop note: {note}")
#         print(note[1])
