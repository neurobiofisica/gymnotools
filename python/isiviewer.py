#-*- encoding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import struct, re, sys, os
import cPickle as pickle

samplingrate = 50000
spksamples = 256
nchannels = 7
maxamp = 9

def spikerange(recog, i, start, end):
    l = []
    while i > 0:
        fish,pos = recog[i]
        if pos < start:
            break
        i -= 1
    while i < recog.shape[0]:
        fish,pos = recog[i]
        if pos > end:
            break
        l.append((fish,pos))
        i += 1
    return l

class SigFig:
    def __init__(self, filename, recog):
        self.fig = plt.figure()
        self.ax  = [self.fig.add_subplot(nchannels,1,1)]
        self.ax += [self.fig.add_subplot(nchannels,1,i, sharex=self.ax[0]) for i in xrange(2,nchannels+1)]
        self.p = [None for i in xrange(nchannels)]
        self.spk = []

        for ax in self.ax[:-1]:
            plt.setp(ax.get_xticklabels(), visible=False)
            plt.setp(ax.xaxis.get_offset_text(), visible=False)
        for ax in self.ax:
            ax.yaxis.set_major_locator(plt.MaxNLocator(3))
        
        for i in xrange(nchannels):
            self.ax[i].set_ylabel(u'$A_{%d}$ (V)'%i)
        self.ax[-1].set_xlabel(u't (s)')
        
        self.datafile = open(filename, 'rb')
        self.recog = recog

    def draw(self):
        self.fig.canvas.draw()
        
    def clearhist(self):
        toolbar = self.fig.canvas.toolbar
        toolbar._views.clear()
        toolbar._positions.clear()
        toolbar.push_current()
        
    def plotdata(self, offset, nsamples=spksamples):
        f = self.datafile
        f.seek(offset*nchannels*4)
        data = np.frombuffer(f.read(4*nsamples*nchannels), dtype=np.float32)
        nsamples = len(data) // nchannels

        t = np.arange(offset, offset+nsamples)/samplingrate
        axis = [t.min(), t.max(), -maxamp, maxamp]
        
        for p in self.p:
            if p: p.remove()
        for p in self.spk:
            p.remove()
        
        for i in xrange(nchannels):
            ax = self.ax[i]
            self.p[i], = ax.plot(t, data[i::nchannels], 'k-',
                                 scalex=False, scaley=False)
            ax.axis(axis)
            
        return nsamples
            
    def plotspike(self, ind, margin=12*spksamples):
        recog = self.recog
        fish,pos = recog[ind]
        
        start = max(0, pos-margin+spksamples/2)
        nsamples = 2*margin
        nsamples = self.plotdata(start, nsamples)
        
        end = start + nsamples
        l = spikerange(recog, ind, start, end)
        
        spk = []
        self.spk = spk
        cpos, cfish = pos, fish
        for i in xrange(nchannels):
            ax = self.ax[i]
            ax.set_autoscale_on(False)
            for fish,pos in l:
                start = pos / samplingrate
                end = (pos + spksamples) / samplingrate
                color = 'r' if fish==1 else 'g'
                alpha = .5 if (pos==cpos and fish==cfish) else .3
                spk.append(ax.axvspan(start, end, fc=color, ec=color, alpha=alpha))
        
class ISIFig:
    def __init__(self, sigfig):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1,1,1)
        self.ax.set_xlabel(u't (s)')
        self.ax.set_ylabel(u'ISI (s)')
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.p = []
        self.sopts = {'scalex': True, 'scaley': True}
        self.sigfig = sigfig
        self.recog = sigfig.recog
        
    def onpick(self, event):
        artist = event.artist
        try: fish = 1 if self.p.index(artist)==0 else -1
        except: return
        
        # workaround for matplotlib bug (was need in v0.99.3, now it is fixed)
        #path, affine = event.artist._transformed_path.get_transformed_path_and_affine()
        #x = path.vertices[event.ind[0], 0]
        #xs = self.At if fish==1 else self.Bt
        #ind = abs(xs - x).argmin()        
        ind = event.ind[0]
        
        ind += 1
        ind = int(self.Amap[ind] if fish==1 else self.Bmap[ind])
        self.sigfig.plotspike(ind)
        self.sigfig.draw()
        self.sigfig.clearhist()
        
    def draw(self):
        self.fig.canvas.draw()
        
    def calc(self):
        recog = self.recog
        nA = sum(recog[:,0] == 1)
        nB = recog.shape[0] - nA
        self.Amap = np.zeros(nA, dtype=np.uint)
        self.Bmap = np.zeros(nB, dtype=np.uint)
        self.At = np.zeros(nA)
        self.Bt = np.zeros(nB)
        self.A = np.zeros(nA-1)
        self.B = np.zeros(nB-1)
        Amap, Bmap, At, Bt, A, B = self.Amap, self.Bmap, self.At, self.Bt, self.A, self.B
        iA, iB = 0, 0
        for i in xrange(recog.shape[0]):
            fish,pos = recog[i]
            if fish == 1:
                Amap[iA] = i
                At[iA] = pos / samplingrate
                if iA > 0: A[iA-1] = At[iA] - At[iA-1]
                iA += 1
            else:
                Bmap[iB] = i
                Bt[iB] = pos / samplingrate
                if iB > 0: B[iB-1] = Bt[iB] - Bt[iB-1]
                iB += 1
                
    def plot(self):
        ax = self.ax
        for p in self.p:
            if p: p.remove()
        self.p = [ax.plot(self.At[1:], self.A, 'r.-', picker=5, **self.sopts)[0],
                  ax.plot(self.Bt[1:], self.B, 'g.-', picker=5, **self.sopts)[0]]
        #self.p = [ax.plot(self.A, 'r.-', picker=5, **self.sopts)[0],
         #         ax.plot(self.B, 'g.-', picker=5, **self.sopts)[0]]
        self.sopts = {'scalex': False, 'scaley': False}
        
        
def main():
    datafile = sys.argv[1]     # I32 data file
    recogfile = sys.argv[2]    # generated by recog export
    recog = np.loadtxt(recogfile, dtype=np.int)
    sigfig = SigFig(datafile, recog)
    isifig = ISIFig(sigfig)
    isifig.calc()
    isifig.plot()
    plt.show()

if __name__ == '__main__':
    main()
