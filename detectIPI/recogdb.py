import struct
import numpy as np

NumChannels = 11

def fishwin(bindata):
    off, size = struct.unpack('ii', bindata[:8])
    bindata = bindata[8:]
    dataitems = NumChannels * size
    datalen = dataitems * 4
    data = np.frombuffer(bindata[:datalen], dtype=np.float32)
    bindata = bindata[datalen:]
    data = data.reshape((NumChannels, size))
    return (off, data), bindata

def fishrec(tup):
    off, bindata = tup
    off, = struct.unpack('q', off)
    presentFish, direction, distA, distB, distAB, flags, svm, pairsvm, probA, probB = struct.unpack('=iifffiiqff', bindata[:44])
    svm = chr(svm)
    #print '%d\t%d\t%f\t%f\t%f\t%d\t%c\t%d\t%f\t%f\n'%(off,presentFish,distA,distB,distAB,flags,svm,pairsvm,probA,probB)
    bindata = bindata[44:]
    fishwins = {}
    if presentFish & 1:
        fishwins['A'], bindata = fishwin(bindata)
    if presentFish & 2:
        fishwins['B'], bindata = fishwin(bindata)
    return off, direction, distA, distB, distAB, flags, svm, pairsvm, probA, probB, fishwins

def getDataFromDb(db,k):
    key = struct.pack('q',k)
    for rec in db.iteritems():
        off, bindata = rec
        if off == key:
            return fishrec(rec)
