# -*- encoding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import sys, bsddb3, recogdb

NumChannels = 7
SamplingRate = 50e3
BytesPerSample = NumChannels*4

db = bsddb3.btopen(sys.argv[1], 'r')

unit = sys.argv[3]
assert(unit in ('seconds', 'samples'))

if unit == 'seconds':
    searchoff = int(float(sys.argv[2]) * SamplingRate * BytesPerSample)
else:
    searchoff = int(sys.argv[2])

for rec in db.iteritems():
    off, distA, distB, distAB, fishwins = recogdb.fishrec(rec)
    if off >= searchoff:
        print repr(('off', off))
        print repr(('distA', distA))
        print repr(('distB', distB))
        print repr(('distAB', distAB))
        print repr(('fishwins', fishwins))
        break

