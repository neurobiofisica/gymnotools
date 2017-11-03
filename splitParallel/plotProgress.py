#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import sys

for num in range(8):

    name = '/ramdisk/%d.timestamps'%num

    A = np.loadtxt(name, unpack=True)
    #freq = 50000.
    freq = 1

    P1 = A[1][ A[0]==1 ] / freq
    P2 = A[1][ A[0]==-1 ] / freq

    plt.subplot(8,1,num+1)

    plt.plot(P1[1:], np.diff(P1), 'C0.-')
    plt.plot(P2[1:], np.diff(P2), 'C3.-')

    ymin = 0.013
    ymax = 0.018

    ymin *= 50000
    ymax *= 50000

    plt.ylim( (ymin, ymax) )


#plt.tight_layout()
plt.show()
