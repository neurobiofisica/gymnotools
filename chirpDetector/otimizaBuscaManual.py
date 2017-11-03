import numpy as np
import matplotlib.pyplot as plt
import sys

CHIRPONOFF = 20

nchan = 11
idx0 = 0
freq = 45454.545454
winsize = int(0.5*freq)

if sys.argv[1] not in ['-b', '-e']:
    print('first argument must be -b or -e')
    sys.exit(-1)

S = np.memmap(sys.argv[2], mode='r', dtype=np.float32)
Cb, Ce = np.loadtxt(sys.argv[3], dtype=np.int, unpack=True)

if sys.argv[1] == '-b':
    C = Cb
    out = open(sys.argv[3] + '_corr_b', 'a')
    win = winsize
else:
    C = Ce
    out = open(sys.argv[3] + '_corr_e', 'a')
    win = -1*winsize

fig = plt.figure(1, figsize=(26,14))
ax = fig.add_subplot(111)
l = []
for i in range(nchan):
    ltmp, = ax.plot([], []) 
    l.append(ltmp)
ax.plot([], 'ko', mew=5, label='\'d\' Dots on', zorder=CHIRPONOFF)

class Geral(object):
    def __init__(self, fig, ax, lines, idx0):
        self.fig = fig
        self.ax = ax
        self.l = lines
        self.idx = idx0-1
        self.c = C[self.idx]
        fig.canvas.mpl_connect('button_press_event', self.bpress)
        self.nex()

    def bpress(self, event):
        pos = int(event.xdata)
        out.write('%d\n'%pos)
        out.flush()
        self.nex()

    def nex(self):
        self.idx += 1
        self.c = C[self.idx]
        for i in range(nchan):
            sig = S[ i + nchan*min(self.c, self.c+win) : i + nchan*max(self.c, self.c+win) : nchan ]
            self.l[i].set_ydata(3*i + 3*sig)
            self.l[i].set_xdata( np.linspace(min(self.c, self.c+win), max(self.c, self.c+win), sig.size) )
        self.ax.set_title( '%d - %d'%(self.idx, C.size) )
        self.ax.set_xlim( (min(self.c, self.c+win), max(self.c, self.c+win)) )
        self.ax.set_ylim( (-10, 3*nchan+10) )
        self.fig.canvas.draw()
    
callback = Geral(fig, ax, l, idx0)

#axNext = plt.axes([0.8, 0.05, 0.1, 0.075])

#bNext = Button(axNext, 'Next')

#bNext.on_clicked(callback.nex)

'''for n in range(idx0, C.size):
    c = C[n]
    for i in range(nchan):
        sig = S[ i + nchan*c : i + nchan*(c+win) : nchan ]
        l[i].set_ydata(3*i + sig)
        l[i].set_xdata( np.linspace(min(c, c+win), max(c, c+win), sig.size) )
    ax.set_title( '%d - %d'%(n, C.size) )
    ax.set_xlim( (min(c, c+win), max(c, c+win)) )
    ax.set_ylim( (-10, 3*nchan+10) )
    plt.show()'''
plt.show()
