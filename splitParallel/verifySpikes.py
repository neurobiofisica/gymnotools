#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from matplotlib.widgets import Slider,Button

win = 10000
beg = int( 36759800-(win//2) )
step = 3
typMinSize = 12/step # Samples
typMaxSize = 120/step # Samples
hmin = 0.10
freq = 50000.

locsFile = 'locs_0.npy'
hilbFile = '0.hilb'

L = np.load(locsFile)

H = np.fromfile(hilbFile, dtype=np.float32)
h = H[beg:beg+win]

fig = plt.figure(1)
ax = plt.axes([0.05,0.25,0.9,0.7])

sig = scipy.signal.decimate(h,step,zero_phase=True)

widths=np.arange(typMinSize, typMaxSize,0.10)
locs_now = step*beg + step*scipy.signal.find_peaks_cwt(sig, widths,noise_perc=10)


def update(val):

    pos1 = next(n for n,val in enumerate(L) if val > beg)
    pos2 = next(n for n,val in enumerate(L) if val > beg+win)
    locs_now = L[pos1:pos2]

    ax.clear()

    ax.plot(np.linspace(beg,beg+win,h.size), h,'g-')
    for l in locs_now:
        ax.plot( (l,l), (0,5), 'k-')

axNext = plt.axes([0.90,0.1,0.05,0.05])
bNext = Button(axNext, 'Next')
def nextB(ev):
    global beg
    beg += int(0.9*win)

    h = H[beg:beg+win]

    pos1 = next(n for n,val in enumerate(L) if val > beg)
    pos2 = next(n for n,val in enumerate(L) if val > beg+win)
    locs_now = L[pos1:pos2]

    ax.clear()

    ax.plot(np.linspace(beg,beg+win,h.size), h,'g-')
    for l in locs_now:
        ax.plot( (l,l), (0,5), 'k-')
bNext.on_clicked(nextB)

axPrev = plt.axes([0.05,0.1,0.05,0.05])
bPrev = Button(axPrev, 'Prev')
def prevB(ev):
    global beg
    beg += int(0.9*win)

    h = H[beg:beg+win]

    pos1 = next(n for n,val in enumerate(L) if val > beg)
    pos2 = next(n for n,val in enumerate(L) if val > beg+win)
    locs_now = L[pos1:pos2]

    ax.clear()

    ax.plot(np.linspace(beg,beg+win,h.size), h,'g-')
    for l in locs_now:
        ax.plot( (l,l), (0,5), 'k-')
bPrev.on_clicked(prevB)

update(0)

plt.show()
