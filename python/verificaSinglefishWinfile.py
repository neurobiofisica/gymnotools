from __future__ import division
import windowfile
import numpy as np
import sys

A = np.loadtxt(sys.argv[1], unpack=True)
offs = list( windowfile.readwinsEx2(open(sys.argv[2], 'r')) )

offnow = -1
idxOff = -1
tam = A.shape[1]
for n in range(tam):
    if n % 100 == 0 or True:
        sys.stdout.write('\r%d\t%.03f%%'%( n, 100.*n / tam) )
        sys.stdout.flush()
    P = A[:,n]
    idx = np.argmin( P )
    while offnow != P[idx]:
        idxOff += 1
        offnow =  offs[idxOff]

    if P[1-idx] != offs[idxOff+1]:
        print('\n')
        print(idxOff)
        print('%d-%d\t%d-%d-%d-%d'%(P[0], P[1], offs[idxOff-1], offs[idxOff], offs[idxOff+1], offs[idxOff+2] ))
        #sys.exit(-1)
