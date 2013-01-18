# -*- encoding: utf-8 -*-
import numpy as np
import sys, struct, bsddb3, recogdb

NumChannels = 7

db = bsddb3.btopen(sys.argv[1], 'r')
winfile = open(sys.argv[2],'rb')
checkfish = sys.argv[3]
checkfile = open(sys.argv[4],'rb')
threshold = float(sys.argv[5])

assert(checkfish in ('A', 'B'))

for rec in db.iteritems():
    off, distA, distB, distAB, fishwins = recogdb.fishrec(rec)
    wlastlen, = struct.unpack('i', winfile.read(4))
    woff, wsamples, wchannels = struct.unpack('qii', winfile.read(8+4*2))
    winfile.seek(wchannels*(4 + wsamples*4), 1)
    
    assert(off == woff)
    
    checkoff = off/NumChannels
    checkfile.seek(checkoff)
    
    buf = np.frombuffer(checkfile.read(wsamples*4), dtype=np.float32)
    fishexists = 1 if abs(buf).max() >= threshold else 0
    fishdetected = 1 if checkfish in fishwins else 0
    
    if fishexists ^ fishdetected == 1:
        print '%d\t%d\t%d' % (off, fishexists, fishdetected)
