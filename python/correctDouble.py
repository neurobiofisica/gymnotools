#!/usr/bin/env python

import numpy as np
import recogdb
import sys
import struct

freq = 50000.

A = np.loadtxt(sys.argv[1],unpack=True,dtype=np.int)
P1 = A[1][ A[0] == 1]
P2 = A[1][ A[0] ==-1]

DB = recogdb.openDB( sys.argv[2], 'rw')

IPI1 = np.diff(P1) / freq
IPI2 = np.diff(P2) / freq

idx1 = np.where(IPI1 < 0.0002) 
rem1 = P1[idx1]
idx2 = np.where(IPI2 < 0.0002) 
rem2 = P2[idx2]
print(rem1)
print(rem2)

### Remove duplicates
for k in DB.keys():
    raw_data = recogdb.readHeaderEntry(DB, k)
    if raw_data is not None:
        read_data = raw_data[1]
    else:
        continue
    presentFish, direction, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB = read_data
    if correctedPosA in rem1:
        recogdb.delete(DB,k)
        if correctedPosB != -1:
            recogdb.delete(DB,k)
            loc, = struct.unpack('=q',k)
            recogdb.writeEntry(DB, loc, 3, 1, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB, raw_data[2])
            idx, = np.where(rem1 == correctedPosA)
            rem1 = np.delete(rem1,idx)

for k in DB.keys():
    raw_data = recogdb.readHeaderEntry(DB, k)
    if raw_data is not None:
        read_data = raw_data[1]
    else:
        continue
    presentFish, direction, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB = read_data
    if correctedPosB in rem2:
        loc, = struct.unpack('=q',k)
        recogdb.delete(DB,k)
        if correctedPosA != -1:
            recogdb.delete(DB,k)
            loc, = struct.unpack('=q',k)
            recogdb.writeEntry(DB, loc, 3, 1, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB, raw_data[2])
            idx, = np.where(rem2 == correctedPosB)
            rem2 = np.delete(rem2,idx)

print(rem1)
print(rem2)

# Remove the non duplicates
for k in DB.keys():
    raw_data = recogdb.readHeaderEntry(DB, k)
    if raw_data is not None:
        read_data = raw_data[1]
    else:
        continue
    presentFish, direction, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB = read_data
    if correctedPosA in rem1:
        loc, = struct.unpack('=q',k)
        kN, dataN = recogdb.getNearest(DB,1,loc,1)
        kP, dataP = recogdb.getNearest(DB,-1,loc,1)
        correctedPosAN = dataN[recogdb.dicFields['correctedPosA']]
        correctedPosAP = dataP[recogdb.dicFields['correctedPosA']]
        if abs(correctedPosA - correctedPosAN) < abs(correctedPosA - correctedPosAP):
            recogdb.delete(DB,kN)
        else:
            recogdb.delete(DB,kP)


for k in DB.keys():
    raw_data = recogdb.readHeaderEntry(DB, k)
    if raw_data is not None:
        read_data = raw_data[1]
    else:
        continue
    presentFish, direction, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB = read_data
    if correctedPosB in rem2:
        loc, = struct.unpack('=q',k)
        kN, dataN = recogdb.getNearest(DB,1,loc,2)
        kP, dataP = recogdb.getNearest(DB,-1,loc,2)
        correctedPosBN = dataN[recogdb.dicFields['correctedPosB']]
        correctedPosBP = dataP[recogdb.dicFields['correctedPosB']]
        print('delete')
        if abs(correctedPosB - correctedPosBN) < abs(correctedPosB - correctedPosBP):
            recogdb.delete(DB,kN)
        else:
            recogdb.delete(DB,kP)

