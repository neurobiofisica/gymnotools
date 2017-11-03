import numpy as np
import matplotlib.pyplot as plt
from matplotlib.mlab import find
from matplotlib.ticker import FuncFormatter
from matplotlib.widgets import Button
import struct
import sys
import recogdb

around = 0.050
aroundTS = 30
NChan = 11
freq = 45454.545454
key = int(sys.argv[1])
# (hh, mm, ss, uuu) or None


class ChangePos:
    def __init__(self, around, aroundTS, dbName, begkey, Signame, TSName):
        self.lastMove = None

        self.Sig = np.memmap(Signame, dtype=np.float32, mode='r')
        self.SigCh = [self.Sig[i::NChan] for i in range(NChan)]

        ts = np.loadtxt(TSName, unpack=True)
        self.P1 = ts[1][ find(ts[0] == 1) ] / freq
        self.P2 = ts[1][ find(ts[0] ==-1) ] / freq

        self.around = around
        self.aroundTS = aroundTS
        self.key = begkey

        self.db = recogdb.openDB(dbName, 'rw')
        if key != 0:
            self.k = struct.pack('=q', key)
            self.k, self.bindata = self.db.set_location( self.k )
        else:
            self.k, self.bindata = self.db.first()
            self.k, self.bindata = self.db.set_location( self.k )

        self.read_data = recogdb.parseDBHeader( self.bindata )
        self.off, = struct.unpack('=q', self.k)
        print('key:\t%d'%self.off)
        print('time: %s'%self.sec2hms(self.off/freq, None))
        for a,b in recogdb.dicFields.items():
            print('%s:\t%s'%(a, self.read_data[b]))

        self.formatterX = FuncFormatter(self.sec2hms)

        self.f = plt.figure(1, figsize=(25,20))
        self.ax1 = self.f.add_subplot(111)
        self.sigs = [None for i in range(NChan)]
        for i in range(NChan):
            self.sigs[i], = self.ax1.plot((), (), 'k-')
        self.P1Lines = [None for j in range(self.aroundTS)]
        self.P2Lines = [None for j in range(self.aroundTS)]
        for j in range(self.aroundTS):
            self.P1Lines[j], = self.ax1.plot((0,0), (-10, 5*(NChan+1)) , 'b-', alpha=0.4)
            self.P2Lines[j], = self.ax1.plot((0,0), (-10, 5*(NChan+1)) , 'r-', alpha=0.4)
        self.strongLine, = self.ax1.plot( (0,0), (-10, 5*(NChan+1)), 'k-')
        self.newLine, = self.ax1.plot((0, 0), (-10, 5*(NChan+1)), 'k-')

        self.f.canvas.mpl_connect('button_press_event', self.spikeClick)
        self.f.canvas.mpl_connect('motion_notify_event', self.spikeMove)
        self.f.canvas.mpl_connect('button_release_event', self.spikeRelease)

        self.init_data()
        self.plotStuff()
        self.makeButtons()
        self.adjustAxes()


    def init_data(self):

        self.newloc = None

        if self.read_data[ recogdb.dicFields['presentFish'] ] == 1:
            self.txtField = 'correctedPosA'
            self.field = recogdb.dicFields[self.txtField]
        elif self.read_data[ recogdb.dicFields['presentFish'] ] == 2:
            self.txtField = 'correctedPosB'
            self.field = recogdb.dicFields[self.txtField]
        else:
            if self.lastMove == 'prev':
                print( 'Moving to next single spike' )
                self.dbprev(None)
            elif self.lastMove == 'next':
                print( 'Moving to next single spike' )
                self.dbnext(None)
            else:
                print('Only implemmented for non overlapping spikes') 
                self.db.close()
                sys.exit(-1)


        self.begt = self.read_data[ self.field ]/freq - self.around
        self.beg = int(self.begt*freq)
        self.end = self.beg + int(2*self.around*freq)

        self.presentFish = self.read_data[ recogdb.dicFields['presentFish'] ]


    def spikeClick(self, event):
        if event.inaxes == self.ax1:
            self.newLine.set_xdata( (event.xdata, event.xdata) )
            self.f.canvas.draw()

    def spikeMove(self, event):
        if event.inaxes == self.ax1:
            if event.button == 1:
                self.newLine.set_xdata( (event.xdata, event.xdata) )
                self.f.canvas.draw()
    def spikeRelease(self, event):
        if event.inaxes == self.ax1:
            self.newloc = event.xdata

    def sec2hms(self, x, pos):
        t = int(round(1e4*x))
        s, ms = divmod(t, 1e4) 
        m, s = divmod(x, 60)
        h, m = divmod(m, 60)
        return '%02d:%02d:%02d.%04d' % (h, m, s, ms)

    def plotStuff(self):
        idxTS1 = next(n for n,p in enumerate(self.P1) if p > self.begt) - 1
        idxTS2 = next(n for n,p in enumerate(self.P2) if p > self.begt) - 1

        for i in range(NChan):
            locSig = self.SigCh[i][self.beg:self.end]
            X = np.linspace(self.begt, self.begt+2*self.around, locSig.size)

            self.sigs[i].set_xdata(X)
            self.sigs[i].set_ydata( 5*i + locSig )

        for j in range(self.aroundTS):
            X1 = self.P1[ idxTS1+j ]
            self.P1Lines[j].set_xdata( (X1,X1) )
            X2 = self.P2[ idxTS2+j ]
            self.P2Lines[j].set_xdata( (X2,X2) )

        if self.presentFish == 1:
            color = 'b'
        elif self.presentFish == 2:
            color = 'r'
        else:
            color = 'g'
        self.strongLine.set_xdata( (self.begt+self.around, self.begt+self.around) )
        self.strongLine.set_color( color )
        #self.ax1.plot( (self.begt+self.around, self.begt+self.around), (-10, 5*(NChan+1)), '-', color=color)

        if self.presentFish == 1:
            color = 'c'
        elif self.presentFish == 2:
            color = 'm'
        else:
            color = 'g'
        self.newLine.set_color(color)

        self.f.canvas.draw()

    def makeButtons(self):
        self.axPrev = plt.axes([0.01, 0.05, 0.1, 0.075])
        self.bPrev = Button(self.axPrev, 'Previous')
        self.bPrev.on_clicked(self.dbprev)

        self.axNext = plt.axes([0.11, 0.05, 0.1, 0.075])
        self.bNext = Button(self.axNext, 'Next')
        self.bNext.on_clicked(self.dbnext)

        self.axAccept = plt.axes([0.81, 0.05, 0.1, 0.075])
        self.bAccept = Button(self.axAccept, 'Accept')
        self.bAccept.on_clicked(self.accept)

    def adjustAxes(self):
        self.ax1.set_xlim( (self.begt, self.begt+2*self.around) )
        self.ax1.xaxis.set_major_formatter(self.formatterX)
        self.f.canvas.draw()

    def dbprev(self, event):
        self.lastMove = 'prev'
        self.k, self.bindata = self.db.previous()
        self.read_data = recogdb.parseDBHeader( self.bindata )
        self.off, = struct.unpack('=q', self.k)
        print('\nkey:\t%d'%self.off)
        print('time: %s'%self.sec2hms(self.off/freq, None))
        for a,b in recogdb.dicFields.items():
            print('%s:\t%s'%(a, self.read_data[b]))
        self.init_data()
        self.plotStuff()
        self.adjustAxes()

    def dbnext(self, event):
        self.lastMove = 'next'
        self.k, self.bindata = self.db.next()
        self.read_data = recogdb.parseDBHeader( self.bindata )
        self.off, = struct.unpack('=q', self.k)
        print('\nkey:\t%d'%self.off)
        print('time: %s'%self.sec2hms(self.off/freq, None))
        for a,b in recogdb.dicFields.items():
            print('%s:\t%s'%(a, self.read_data[b]))
        self.init_data()
        self.plotStuff()
        self.adjustAxes()

    def accept(self, event):
        if self.newloc is not None:
            oldCorrectedPos = self.read_data[ self.field ]
            newCorrectedPos = int(self.newloc*freq)
            recogdb.updateHeaderEntry(self.db, self.k, self.txtField, newCorrectedPos, sync=True)
            print('\n\nPLEASE RUN RECOG EXPORT\n\n')

    '''if newloc is not None:
        ax1.plot( (newloc,newloc), (-10, 5*(NChan+1)), 'g-')

    ax1.set_xlim( (begt, begt+2*around) )
    ax1.xaxis.set_major_formatter(formatterX)

    if newloc is not None:
        def accept(event):
            oldCorrectedPos = read_data[ field ]
            newCorrectedPos = int(newloc*freq)
            recogdb.updateHeaderEntry(db, k, txtField, newCorrectedPos, sync=True)
            print('\n\nPLEASE RUN RECOG EXPORT\n\n')

        axAccept = plt.axes([0.81, 0.05, 0.1, 0.075])
        bAccept = Button(axAccept, 'Accept')
        bAccept.on_clicked(accept)


    plt.show()
    return ret

ret = plotCorr('key', key)
print(repr(ret))
while ret is not None:
    print('foda')
    ret = plotCorr(ret, None)
    print(ret)'''


changePos = ChangePos( around, aroundTS, '/ssd/Junho2016/16428000_512.db', key, '/ssd/Junho2016/16428000.abf.memampf32', '/ssd/Junho2016/16428000_512.timestamps')
plt.show()
