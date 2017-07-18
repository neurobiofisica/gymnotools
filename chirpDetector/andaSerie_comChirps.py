import sys,os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

sys.path.append( os.path.abspath('..') )
from read_param import *
# import NChan, freq, winSize

chirps = np.load('chirps.npy')

A = np.memmap(sys.argv[1], dtype='float32')

winSize = int(freq * 0.5)

ch = []
for i in range(nChan):
    ch.append(A[i::nChan])

lines = []

f = plt.figure(1)
ax = f.add_subplot(111)
ax.set_title('0')
for i in range(nChan):
    l, = plt.plot(5*i + ch[i][0:0+winSize])
    lines.append(l)
x = np.arange(winSize).repeat(2)
y = 60*chirps[0:0+winSize].repeat(2)
c, = plt.plot(x,y,'k-', alpha=0.3)

plt.xlim([0,winSize])

class Index(object):
    ind = 0

    def next(self, event):
        self.ind += 1
        ax.set_title('%d - %f%%'%(self.ind*winSize, 100*self.ind*winSize/ch[0].size))
        for i in range(nChan):
            lines[i].set_ydata(5*i + ch[i][winSize*self.ind:winSize*(self.ind+1)])
        c.set_ydata( 60*chirps[winSize*self.ind:winSize*(self.ind+1)].repeat(2) )
        plt.draw()
        
    def prev(self, event):
        self.ind -= 1
        ax.set_title('%d - %f%%'%(self.ind*winSize, 100*self.ind*winSize/ch[0].size))
        for i in range(nChan):
            lines[i].set_ydata(5*i + ch[i][winSize*self.ind:winSize*(self.ind+1)])
        c.set_ydata( 60*chirps[winSize*self.ind:winSize*(self.ind+1)].repeat(2) )
        plt.draw()

callback = Index()
axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
bnext = Button(axnext, 'Next')
bnext.on_clicked(callback.next)
bprev = Button(axprev, 'Previous')
bprev.on_clicked(callback.prev)

plt.show()
