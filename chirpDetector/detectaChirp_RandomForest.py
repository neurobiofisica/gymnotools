import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
from sklearn import svm, datasets, ensemble
import sys

if sys.version_info.major == 3:
    xrange = range

def distort(x, baseline=0.2):
    return baseline + (1-baseline)/(1+x**2)


import pickle

nChan = 11
windowSize = 2000
win=100
minsat = -9.9
maxsat = 9.9

clf = pickle.load( open('RandonForestChirpModel_abs.pickle', 'rb') )

out = open(sys.argv[2],'w')

A = np.memmap(sys.argv[1], dtype='float32')
#cut = 3*A.size/10
#cut = int(cut - cut%11)
#A = A[:cut]
channels = [ A[i::11] for i in range(nChan) ]
tam = int(np.ceil(A.size/11))

onChirp = False
chirps = np.zeros( channels[0].size )
step = int(windowSize/10)
consecutive_chirps = 0
consecutive_no = 0
for n,i in enumerate(xrange(0, tam - windowSize, step)):
    if n % (11*10) == 0:
        sys.stdout.write('\r%10d\t\t%3.4f%%'%( i, (100.*i)/tam ))
        sys.stdout.flush()

    sig = np.zeros(windowSize)
    chanused = 0
    for c in xrange(nChan):
        s = channels[c][i:i+windowSize]
        if s.min() < minsat or s.max() > maxsat:
            continue
        sig += np.abs(s)
        chanused += 1

    if chanused == 0:
        print('All saturated')
        for c in xrange(nChan):
            s = channels[c][i:i+windowSize]
            sig += np.abs(s)
    else:
        sig = ((1.*nChan)/chanused) * sig

    sig = sig*distort(sig)
            
    if 1 in clf.predict([sig]):
        consecutive_chirps += 1
        consecutive_no = 0
    else:
        consecutive_chirps = 0
        consecutive_no += 1
        if onChirp == True and consecutive_no > 10:
            onChirp = False
            out.write('\t%d\n'%(i-10))
            out.flush()

    if consecutive_chirps == 4:
        chirps[i-4:i] = 1
        if onChirp == False:
            onChirp = True
            out.write('%d'%(i-4))
    elif consecutive_chirps > 4:
        chirps[i] = 1

print('')
np.save('chirps.npy', chirps)

