import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import sys,os

sys.path.append( os.path.abspath('..') )
from read_param import *
# import NChan, freq, winSize

winsize = int(0.5*freq)

S = np.memmap(sys.argv[1], mode='r', dtype=np.float32)
out = open(sys.argv[1]+'.offs', 'a')

tam = S.size / NChan

class Geral(object):
    def __init__(self, outputfile, fig, ax, lines):
        self.f = outputfile
        self.fig = fig
        self.ax = ax
        self.lines = lines
        self.loc = int(0 * freq)
        self.onChirp = False
        self.plota()

    def isChirp(self, event):
        if self.onChirp == False:
            self.f.write('%d '%(self.loc))
            bChirp.label.set_text('Off end')
        else:
            self.f.write('%d\n'%(self.loc+winsize))
            bChirp.label.set_text('Off begin')
        self.onChirp = not(self.onChirp)
        self.f.flush()

    def nex(self, event):
        self.loc = min( self.loc + winsize, tam-winsize )
        self.plota()

    def prev(self, event):
        self.loc = max( 0, self.loc - winsize)
        self.plota()

    def plota(self):
        for i in range(NChan):
            sig = S[ i + NChan*self.loc : i + NChan*(self.loc+winsize) : NChan ]
            self.lines[i].set_ydata(3*i + sig)
            self.lines[i].set_xdata(np.linspace(self.loc / freq, (self.loc+winsize)/freq,sig.size))
        self.ax.set_xlim( (self.loc/freq, (self.loc+winsize)/freq) )
        self.ax.set_ylim( (-5, 35))#3*NChan+10) )
        self.ax.set_title('%.03f%%'%(100.*self.loc / (1.*tam)))
        self.fig.canvas.draw()



f = plt.figure(1, figsize=(26,14))
ax = f.add_subplot(111)
l = []
for i in range(NChan):
    ltmp, = ax.plot([], [])
    l.append(ltmp)

callback = Geral(out, f, ax, l)

axChirp = plt.axes([0.69, 0.05, 0.1, 0.075])
axNext = plt.axes([0.8, 0.05, 0.1, 0.075])
axPrev = plt.axes([0.91, 0.05, 0.1, 0.075])

bChirp = Button(axChirp, 'Chirp begin')
bNext = Button(axNext, 'Next')
bPrev = Button(axPrev, 'Previous')

bChirp.on_clicked(callback.isChirp)
bNext.on_clicked(callback.nex)
bPrev.on_clicked(callback.prev)

plt.show()
