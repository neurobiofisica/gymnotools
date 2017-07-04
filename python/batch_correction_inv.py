import numpy as np
import recogdb
import struct
import sys

keybeg = 165181307
keyend = 165280258

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

    if oldFish == 1:
        newFish = 2
        newCorrectedPosA = -1
        newCorrectedPosB = oldCorrectedPosA
        newDistA = float('Inf')
        newDistB = 0.
        newDistAB = float('Inf')
    elif oldFish == 2:
        newFish = 1
        newCorrectedPosA = oldCorrectedPosB
        newCorrectedPosB = -1
        newDistA = 0.
        newDistB = float('Inf')
        newDistAB = float('Inf')
    else:
        newFish = 3
        newCorrectedPosA = oldCorrectedPosB
        newCorrectedPosB = oldCorrectedPosA
        newDistA = float('Inf')
        newDistB = float('Inf')
        newDistAB = 0.

    recogdb.updateHeaderEntry(db, key, 'presentFish', newFish, sync=False)
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
