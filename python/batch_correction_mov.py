import numpy as np
import recogdb
import struct
import sys

freq = 50000.

fish = 2
keybeg = 169451424
keyend = 169498558
mov = -0.0028 #ms
mov = int(mov*freq)


db = recogdb.openDB('/ssd/Junho2016/16428000_512.db', 'rw')

kb = struct.pack('=q', keybeg)
ke = struct.pack('=q', keyend)

off, bindata = db.set_location(kb)
off, = struct.unpack('=q', off)
read_data = recogdb.parseDBHeader(bindata)

while (off <= keyend):
    key = recogdb.verifyKey(db, off)
    sys.stdout.write('%d\r'%off)
    sys.stdout.flush()

    oldFish = read_data[ recogdb.dicFields['presentFish'] ]
    oldCorrectedPosA = read_data[ recogdb.dicFields['correctedPosA'] ]
    oldCorrectedPosB = read_data[ recogdb.dicFields['correctedPosB'] ]
    oldDistA = read_data[ recogdb.dicFields['distA'] ]
    oldDistB = read_data[ recogdb.dicFields['distB'] ]
    oldDistAB = read_data[ recogdb.dicFields['distAB'] ]

    if oldFish == 1 and oldFish == fish:
        newCorrectedPosA = oldCorrectedPosA + mov
        newCorrectedPosB = oldCorrectedPosB
        newDistA = 0.
        newDistB = float('Inf')
        newDistAB = float('Inf')
    elif oldFish == 2 and oldFish == fish:
        newCorrectedPosA = oldCorrectedPosA
        newCorrectedPosB = oldCorrectedPosB + mov
        newDistA = float('Inf')
        newDistB = 0.
        newDistAB = float('Inf')
    else:
        if fish == 1:
            newCorrectedPosA = oldCorrectedPosA + mov
            newCorrectedPosB = oldCorrectedPosB
        else:
            newCorrectedPosA = oldCorrectedPosA
            newCorrectedPosB = oldCorrectedPosB + mov
        newDistA = float('Inf')
        newDistB = float('Inf')
        newDistAB = 0.

    recogdb.updateHeaderEntry(db, key, 'correctedPosA', newCorrectedPosA, sync=False)
    recogdb.updateHeaderEntry(db, key, 'correctedPosB', newCorrectedPosB, sync=False)
    recogdb.updateHeaderEntry(db, key, 'distA', newDistA, sync=False)
    recogdb.updateHeaderEntry(db, key, 'distB', newDistB, sync=False)
    recogdb.updateHeaderEntry(db, key, 'distAB', newDistAB, sync=True)

    off, bindata = db.next()
    off, = struct.unpack('=q', off)
    read_data = recogdb.parseDBHeader(bindata)

print('\n')
db.close()
