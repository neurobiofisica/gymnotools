#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from matplotlib.widgets import Slider,Button

win = 10000
beg = int( 2210530-(win//2) )
step = 3
typMinSize = 12/step # Samples
typMaxSize = 120/step # Samples
hmin = 0.10
freq = 50000.

hilbFile = '2.hilb'

H = np.fromfile(hilbFile, dtype=np.float32)
h = H[beg:beg+win]

fig = plt.figure(1)
ax = plt.axes([0.05,0.25,0.9,0.7])

sig = scipy.signal.decimate(h,step,zero_phase=True)

widths=np.arange(typMinSize, typMaxSize,0.10)
locs_now = step*beg + step*scipy.signal.find_peaks_cwt(sig, widths,noise_perc=10)

axstep = plt.axes([0.2,0.15,0.6,0.03])
sstep = Slider(axstep, 'Step', 0.01,1, valinit=0.10)
axnoise = plt.axes([0.2,0.20,0.6,0.03])
snoise = Slider(axnoise, 'Noise', 1,100, valinit=10)
axmin = plt.axes([0.2,0.10,0.6,0.03])
smin = Slider(axmin, 'Min', 1,20, valinit=typMinSize)
axmax = plt.axes([0.2,0.05,0.6,0.03])
smax = Slider(axmax, 'Max', 10,200, valinit=typMaxSize)

    

locs_now = []

def update(val):
    m = smin.val
    M = smax.val
    s = sstep.val
    n = snoise.val
    global locs_now

    widths=np.arange(m, M, s)
    locs_now = step*scipy.signal.find_peaks_cwt(sig, widths,noise_perc=n)
    #locs_now = scipy.signal.argrelmax(h,order=int(M))

    locs_now = locs_now[ np.where( h[locs_now] > hmin ) ]
    ilocs, = np.where(np.diff(locs_now) > int(0.001*freq))
    locs_now = locs_now[ilocs+1]
    locs_now = np.unique(locs_now)


    ax.clear()

    ax.plot(h,'g-')
    for l in locs_now:
        ax.plot( (l,l), (0,5), 'k-')

smin.on_changed(update)
smax.on_changed(update)
sstep.on_changed(update)
snoise.on_changed(update)


axNext = plt.axes([0.90,0.1,0.05,0.05])
bNext = Button(axNext, 'Next')
def nextB(ev):
    global beg
    global locs_now
    global h
    global sig
    beg += int(0.9*win)

    h = H[beg:beg+win]
    sig = scipy.signal.decimate(h,step,zero_phase=True)

    update(0)

    ax.clear()

    ax.plot(h,'g-')
    for l in locs_now:
        ax.plot( (l,l), (0,5), 'k-')
bNext.on_clicked(nextB)

axPrev = plt.axes([0.05,0.1,0.05,0.05])
bPrev = Button(axPrev, 'Prev')
def prevB(ev):
    global beg
    global locs_now
    global h
    global sig
    beg -= int(0.9*win)

    h = H[beg:beg+win]
    sig = scipy.signal.decimate(h,step,zero_phase=True)

    update(0)

    ax.clear()

    ax.plot(h,'g-')
    for l in locs_now:
        ax.plot( (l,l), (0,5), 'k-')
bPrev.on_clicked(prevB)

update(0)

plt.show()
