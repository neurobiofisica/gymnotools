import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.mlab import find
import sys, os

sys.path.append( os.path.abspath('..') )
from read_param import *
# import NChan, freq, winSize

idx0 = 0
around = 40

win = int(0.25*freq)

S = np.memmap(sys.argv[1], mode='r', dtype=np.float32)
Ob, Oe = np.loadtxt(sys.argv[2], unpack=True)
A = np.loadtxt(sys.argv[3], unpack=True)
P1 = A[1][ find(A[0] == 1) ]
P2 = A[1][ find(A[0] ==-1) ]
out = open(sys.argv[2] + 'class', 'a')

class Geral(object):
    def __init__(self, outputfile, fig, axes, lines):
        self.f = outputfile
        self.fig = fig
        self.ax1, self.ax2 = axes
        self.l1, self.l2 = lines
        self.idx = idx0-1
        
        self.nex()

    def is1(self, event):
        self.f.write('%d %d %d\n'%(Ob[self.idx], Oe[self.idx], 1))
        self.f.flush()
        self.nex()

    def is2(self, event):
        self.f.write('%d %d %d\n'%(Ob[self.idx], Oe[self.idx],-1))
        self.f.flush()
        self.nex()

    def nex(self):
        self.idx += 1
        self.ob = Ob[self.idx]
        self.oe = Oe[self.idx]
        for i in range(NChan):
            sig1 = S[ i + NChan*min(self.ob-win, self.ob+win) : i + NChan*max(self.ob-win, self.ob+win) : NChan ]
            sig2 = S[ i + NChan*min(self.oe+win, self.oe-win) : i + NChan*max(self.oe+win, self.oe-win) : NChan ]
            self.l1[i].set_ydata(3*i + 3*sig1)
            self.l2[i].set_ydata(3*i + 3*sig2)
            self.l1[i].set_xdata( np.linspace(min(self.ob-win, self.ob+win), max(self.ob-win, self.ob+win), sig1.size) )
            self.l2[i].set_xdata( np.linspace(min(self.oe-win, self.oe+win), max(self.oe-win, self.oe+win), sig2.size) )

        self.plotLines()

        self.ax1.set_title('%d - %d'%(self.idx, Ob.size))
        self.ax2.set_title('%d - %d'%(self.idx, Oe.size))
        self.ax1.set_xlim( (min(self.ob-win, self.ob+win), max(self.ob-win, self.ob+win)) )
        self.ax2.set_xlim( (min(self.oe-win, self.oe+win), max(self.oe-win, self.oe+win)) )
        self.ax1.set_ylim((-10, 3*NChan+10))
        self.ax2.set_ylim((-10, 3*NChan+10))
        self.fig.canvas.draw()

    def plotLines(self):
        idx1 = next(n for n,p in enumerate(P1) if p > self.ob)             
        idx2 = next(n for n,p in enumerate(P2) if p > self.ob)

        for i in range(around):
            x = P1[idx1-i]
            y = (-10, 3*NChan+10)
            ax1.plot((x,x), y, 'b-', lw=10, alpha=0.3)
            x = P2[idx2-i]
            y = (-10, 3*NChan+10)
            ax1.plot((x,x), y, 'r-', lw=10, alpha=0.3)
        for i in range(around):
            x = P1[idx1+i]
            y = (-10, 3*NChan+10)
            ax1.plot((x,x), y, 'b-', lw=10, alpha=0.3)
            x = P2[idx2+i]
            y = (-10, 3*NChan+10)
            ax1.plot((x,x), y, 'r-', lw=10, alpha=0.3)

        idx1 = next(n for n,p in enumerate(P1) if p > self.oe)
        idx2 = next(n for n,p in enumerate(P2) if p > self.oe)

        for i in range(around):
            x = P1[idx1-i]
            y = (-10, 3*NChan+10)
            ax2.plot((x,x), y, 'b-', lw=10, alpha=0.3)
            x = P2[idx2-i]
            y = (-10, 3*NChan+10)
            ax2.plot((x,x), y, 'r-', lw=10, alpha=0.3)
        for i in range(around):
            x = P1[idx1+i]
            y = (-10, 3*NChan+10)
            ax2.plot((x,x), y, 'b-', lw=10, alpha=0.3)
            x = P2[idx2+i]
            y = (-10, 3*NChan+10)
            ax2.plot((x,x), y, 'r-', lw=10, alpha=0.3)



fig = plt.figure(1, figsize=(26,14))
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)
l1 = []
l2 = []
for i in range(NChan):
    l1tmp, = ax1.plot([], [])
    l2tmp, = ax2.plot([], [])
    l1.append(l1tmp)
    l2.append(l2tmp)

callback = Geral(out, fig, [ax1, ax2], [l1, l2])

ax_is1 = plt.axes([0.8, 0.05, 0.1, 0.075])
ax_is2 = plt.axes([0.91, 0.05, 0.1, 0.075])

b_is1 = Button(ax_is1, 'Blue fish off')
b_is2 = Button(ax_is2, 'Red fish off')

b_is1.on_clicked(callback.is1)
b_is2.on_clicked(callback.is2)

plt.show()
