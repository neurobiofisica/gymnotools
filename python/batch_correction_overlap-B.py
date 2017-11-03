import numpy as np
import recogdb
import struct
import sys

keybeg = 356625319
keyend = 356631058

db = recogdb.openDB(sys.argv[1], 'rw')

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

    if oldFish == 3:
        newFish = 2
        newCorrectedPosA = -1
        newCorrectedPosB = oldCorrectedPosB
        newDistA = float('Inf')
        newDistB = 0.
        newDistAB = float('Inf')

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
