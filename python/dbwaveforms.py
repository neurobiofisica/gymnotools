import matplotlib.pyplot as plt
import numpy as np
import sys, bsddb3, recogdb

db = bsddb3.btopen(sys.argv[1], 'r')

searchoff = np.inf
if len(sys.argv) >= 3:
    searchoff = int(sys.argv[2])

A = [list([]) for i in xrange(7)]
B = [list([]) for i in xrange(7)]

mark = None

for rec in db.iteritems():
    off, distA, distB, distAB, fishwins = recogdb.fishrec(rec)
    if mark == None and off >= searchoff:
        print(repr(('mark', off, distA, distB, distAB)))
        mark = sum(map(len,A[0]))
    dataA = fishwins['A'][1] if 'A' in fishwins else np.zeros((7,0))
    dataB = fishwins['B'][1] if 'B' in fishwins else np.zeros((7,0))
    arrsz = max(dataA.shape[1], dataB.shape[1]) + 2
    apszA = arrsz - dataA.shape[1]
    apszB = arrsz - dataB.shape[1]
    dataA = np.concatenate((dataA, np.nan*np.ones((7,apszA))),1)
    dataB = np.concatenate((dataB, np.nan*np.ones((7,apszB))),1)
    [A[i].append(dataA[i,:]) for i in xrange(7)]
    [B[i].append(dataB[i,:]) for i in xrange(7)]

A = map(np.concatenate, A)
B = map(np.concatenate, B)

ax=plt.subplot(14,1,1)
plt.plot(A[0],'r',alpha=.4)
plt.plot(B[0],'g',alpha=.4)
plt.plot([mark,mark],[-10,10],'b')
for i in xrange(1,7):
    plt.subplot(7,1,i+1,sharex=ax)
    plt.plot(A[i],'r',alpha=.4)
    plt.plot(B[i],'g',alpha=.4)
    plt.plot([mark,mark],[-10,10],'b')
plt.show()
        
        