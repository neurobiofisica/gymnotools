# -*- encoding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import sys, bsddb3, recogdb

NumChannels = 11

db = bsddb3.btopen(sys.argv[1], 'r')

searchoff = np.inf
if len(sys.argv) >= 3:
    searchoff = int(sys.argv[2])

A = [list([]) for i in xrange(NumChannels)]
B = [list([]) for i in xrange(NumChannels)]

mark = None

for rec in db.iteritems():
    off, distA, distB, distAB, fishwins = recogdb.fishrec(rec)
    if mark == None and off >= searchoff:
        print(repr(('mark', off, distA, distB, distAB)))
        mark = sum(map(len,A[0]))
    dataA = fishwins['A'][1] if 'A' in fishwins else np.zeros((NumChannels,0))
    dataB = fishwins['B'][1] if 'B' in fishwins else np.zeros((NumChannels,0))
    arrsz = max(dataA.shape[1], dataB.shape[1]) + 2
    apszA = arrsz - dataA.shape[1]
    apszB = arrsz - dataB.shape[1]
    dataA = np.concatenate((dataA, np.nan*np.ones((NumChannels,apszA))),1)
    dataB = np.concatenate((dataB, np.nan*np.ones((NumChannels,apszB))),1)
    for i in xrange(NumChannels):
        A[i].append(dataA[i,:])
        B[i].append(dataB[i,:])

A = map(np.concatenate, A)
B = map(np.concatenate, B)

ax=plt.subplot(NumChannels,1,1)
plt.plot(A[0],'r',alpha=.4)
plt.plot(B[0],'g',alpha=.4)
plt.plot([mark,mark],[-10,10],'b')
plt.setp(ax.axes.get_xaxis(), visible=False)
plt.axis([0, len(A[0]), -10, 10])
for i in xrange(1,NumChannels):
    axx=plt.subplot(NumChannels,1,i+1,sharex=ax)
    plt.plot(A[i],'r',alpha=.4)
    plt.plot(B[i],'g',alpha=.4)
    plt.plot([mark,mark],[-10,10],'b')
    plt.setp(axx.axes.get_xaxis(), visible=False)
    plt.axis([0, len(A[0]), -10, 10])

plt.show()
        
        
