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
    presentFish, distA, distB, distAB, flags, svm, probA, probB = struct.unpack('ifffiiff', bindata[:20])
    bindata = bindata[20:]
    fishwins = {}
    if presentFish & 1:
        fishwins['A'], bindata = fishwin(bindata)
    if presentFish & 2:
        fishwins['B'], bindata = fishwin(bindata)
    return off, distA, distB, distAB, flags, svm, probA, probB, fishwins
