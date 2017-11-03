#!/usr/env python

import recogdb
import numpy as np
import sys
import struct

nproc = 8
nchan = 7

A = np.memmap(sys.argv[1], mode='r', dtype=np.float32)
tamChunk = (A.size // nchan) // nproc

DBout = recogdb.openDB('merge.db', 'w')

for i in range(nproc):
    print(i)
    DBin = recogdb.openDB('%d.db'%i, 'r')

    pos = i*tamChunk
    
    for k in DBin.keys():
        key, = struct.unpack('=q',k)
        key += pos
        codedkey = struct.pack('=q',key)

        off, read_data, spkdata = recogdb.readHeaderEntry(DBin, k)
        read_data = list(read_data)
        if read_data[ recogdb.dicFields['presentFish'] ] == 1:
            read_data[ recogdb.dicFields['correctedPosA'] ] += pos
        elif read_data[ recogdb.dicFields['presentFish'] ] == 2:
            read_data[ recogdb.dicFields['correctedPosB'] ] += pos
        if read_data[ recogdb.dicFields['presentFish'] ] == 3:
            read_data[ recogdb.dicFields['correctedPosA'] ] += pos
            read_data[ recogdb.dicFields['correctedPosB'] ] += pos
        data = recogdb.binarizeDBHeader(read_data) + spkdata

        DBout.update( [(codedkey, data), ] )
        #DBout.sync()

    DBout.sync()
    DBin.close()

DBout.close()
