import struct, sys, os
import argparse

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.mlab import find
from matplotlib.ticker import FuncFormatter
from matplotlib.widgets import Button
from matplotlib.backend_bases import MouseEvent, KeyEvent

from PyQt4 import QtCore, QtGui
from graphicalInterface import Ui_Dialog
from IPIWindow import IPIWindow

sys.path.append( os.path.realpath('../') )
import recogdb

# Defines (zorder -> used of selecting picker)
IPIDATABLUE = 100 # The dots will be on top of every other plot
IPIDATARED = 200
LEGENDIPI = 3
LEGENDBLUE = 4
LEGENDRED = 5
SCATTER = 6
OPTIONS = 7

FIGIPI = 1
FIGSIG = 2

# Constants
freq = 45454.545454
NChan = 11

###### Auxiliary funcs ####

# Auxiliary function for reading
def parseSVMFlags(f, col=4):
    flags = []
    for line in f.xreadlines():
        flags.append( line.split()[col] )
    return flags

# make a color from number
# base is a list containing the chars 'r','g','b'
def num2color(num, base):
    c = hex(num)[2:].rjust(2,'0')
    out = '#'
    if 'r' in base:
        out = out + c
    else:
        out = out + '00'
    if 'g' in base:
        out = out + c
    else:
        out = out + '00'
    if 'b' in base:
        out = out + c
    else:
        out = out + '00'
    return out

# Argument parser

class MyParser(argparse.ArgumentParser): # Prints help message in case of error
    def error(self, message):
        self.print_help()
        sys.stderr.write('\nerror: %s\n' %message)
        sys.exit(2)

# Deactivate keyboard shortcuts of matplotlib
for v in plt.rcParams.keys():
    if 'keymap' in v:
        plt.rcParams[v] = ''

class PickPoints:
    lock = None
    def __init__(self, plotObject):

        self.plotObject = plotObject
        self.fig = plotObject.fig
        self.ax = plotObject.ax

        # Auxiliary plots for legend
        self.ax.plot([], 'k-', lw=2, label='\'i\' IPI on', zorder=LEGENDIPI)
        self.ax.plot([], 'b.-', mew=2, label='\'b\' Blue on', zorder=LEGENDBLUE)
        self.ax.plot([], 'r.-', mew=2, label='\'r\' Red on', zorder=LEGENDRED)
        self.ax.plot([], 'ko', mew=5, label='\'d\' Dots on', zorder=SCATTER)
        self.ax.plot([], 'w.', label='\'o\' Options off', zorder=OPTIONS)
        self.ax.legend()
        handles, labels = self.ax.get_legend_handles_labels()

        self.cidpick = self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.cidpress = self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.cidzoom = self.fig.canvas.mpl_connect('scroll_event', self.zoom)
        self.cidbpress = self.fig.canvas.mpl_connect('button_press_event', self.button_press)
        self.cidmotion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cidbrelease = self.fig.canvas.mpl_connect('button_release_event', self.button_release)

        self.b = True
        self.r = True
        self.svm = False
        self.ipi = True
        self.options = False
        #self.plotObject.scatterFlag = True # Ja inicializado na classe PlotData

        self.initialPos = None


        self.dicHandles = {}

        for h in handles:
            if h.zorder == LEGENDBLUE:
                self.dicHandles.update( {'b':h} )
            elif h.zorder == LEGENDRED:
                self.dicHandles.update( {'r':h} )
            elif h.zorder == LEGENDIPI:
                self.dicHandles.update( {'IPI':h} )
            elif h.zorder == SCATTER:
                self.dicHandles.update( {'Dots':h} )
            elif h.zorder == OPTIONS:
                self.dicHandles.update( {'Options':h} )

        self.ind = 0
        self.ylim = self.ax.get_ylim()
        self.end = self.ax.get_xaxis().get_data_interval()[1]
        self.make_buttons()

    def make_buttons(self):
        self.fig.subplots_adjust(bottom=0.15)

        axprev = self.fig.add_axes([0.001, 0.005, 0.1, 0.07])
        axhome = self.fig.add_axes([0.111, 0.005, 0.1, 0.07])
        axnext = self.fig.add_axes([0.221, 0.005, 0.1, 0.07])
        axzoom = self.fig.add_axes([0.899, 0.006, 0.1, 0.07])
        self.bnext = Button(axnext, 'Next')
        self.bnext.on_clicked(self.next)
        self.bprev = Button(axprev, 'Previous')
        self.bprev.on_clicked(self.prev)
        self.bhome = Button(axhome, 'Home')
        self.bhome.on_clicked(self.home)

        self.zoomStatus = 'X'

        self.bzoom = Button(axzoom, self.zoomStatus + ' Zoom')
        self.bzoom.on_clicked(self.click_zoom)

        self.fig.canvas.draw()

    def onpick(self,event):
        if event.mouseevent.button != 1:
            return

        try:
            self.pltsvmstrongB.pop(0).remove()
        except:
            pass
        try:
            self.pltsvmstrongR.pop(0).remove()
        except:
            pass

        zorder = event.artist.zorder
        if self.ipi == True and (\
                (zorder == IPIDATABLUE and self.b == True) or \
                (zorder == IPIDATARED and self.r == True)):

            ind = event.ind[0]

            if self.plotObject.isScatter == False:
                xdata = event.artist.get_xdata()
            else:
                data = event.artist.get_offsets()
                xdata = [x for x,y in data]

            sample = int(round(xdata[ind]*freq))
            key = self.plotObject.offsDic[sample]
            off, data, spkwin = recogdb.readHeaderEntry(self.plotObject.db,key)
            off = off[0]

            if zorder == IPIDATABLUE:
                color = 'b'

                # Draw a SVM pair line
                if data[ recogdb.dicFields['svm'] ] == 's':
                    off2 = data[ recogdb.dicFields['pairsvm'] ]
                    sample2 = self.plotObject.correctedPosDic[off2]
                    self.pltsvmstrongR = self.ax.plot([sample2/freq,sample2/freq],self.plotObject.SVMY[:2],'r-')
                # Draw a line over the point
                self.pltsvmstrongB = self.ax.plot([sample/freq,sample/freq],self.plotObject.SVMY[:2],'b-')

            elif zorder == IPIDATARED:
                color = 'r'

                # Plots SVM Pair line
                if data[ recogdb.dicFields['svm'] ] == 's':
                    off2 = data[ recogdb.dicFields['pairsvm'] ]
                    sample2 = self.plotObject.correctedPosDic[off2]
                    self.pltsvmstrongB = self.ax.plot([sample2/freq,sample2/freq],self.plotObject.SVMY[:2],'b-')
                # Draw a line over the point
                self.pltsvmstrongR = self.ax.plot([sample/freq,sample/freq],self.plotObject.SVMY[:2],'r-')


            Parameters = ( data[ recogdb.dicFields['presentFish'] ], \
                self.plotObject.sec2hms(sample / freq, None), \
                off, \
                data[ recogdb.dicFields['direction'] ], \
                data[ recogdb.dicFields['svm'] ], \
                data[ recogdb.dicFields['probA'] ], \
                data[ recogdb.dicFields['probB'] ], \
                data[ recogdb.dicFields['distA'] ], \
                data[ recogdb.dicFields['distB'] ], \
                data[ recogdb.dicFields['distAB'] ], \
            )

            self.fig.canvas.draw() # To make SVM lines bold
            central = (xdata[ind], color)
            self.plotObject.plotSigData(central)
            if self.options == True:
                self.plotObject.dialogIPI.fillTextBoxes(Parameters)
                self.plotObject.dialogIPI.exec_()

    def press(self,event):
        key = event.key
        sys.stdout.flush()
        if key == 'b':
            self.b = not(self.b)
            if self.b == True:
                self.dicHandles['b'].set_label('\'b\' Blue on')
            else:
                self.dicHandles['b'].set_label('\'b\' Blue off')
        elif key == 'r':
            self.r = not(self.r)
            if self.r == True:
                self.dicHandles['r'].set_label('\'r\' Red on')
            else:
                self.dicHandles['r'].set_label('\'r\' Red off')
        elif key == 's':
            self.svm = not(self.svm)
            if self.svm == True:
                self.dicHandles['SVM'].set_label('\'s\' SVM on')
            else:
                self.dicHandles['SVM'].set_label('\'s\' SVM off')
        elif key == 'i':
            self.ipi = not(self.ipi)
            if self.ipi == True:
                self.dicHandles['IPI'].set_label('\'i\' IPI on')
            else:
                self.dicHandles['IPI'].set_label('\'i\' IPI off')
        elif key == 'd':
            self.plotObject.scatterFlag = not(self.plotObject.scatterFlag)
            if self.plotObject.scatterFlag == True:
                self.dicHandles['Dots'].set_label('\'d\' Dots on')
            else:
                self.dicHandles['Dots'].set_label('\'d\' Dots off')

            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            self.plotObject.plotData(xlim[0],xlim[1])
            self.ax.set_ylim(ylim)
        elif key == 'o':
            self.options = not(self.options)
            if self.options == True:
                self.dicHandles['Options'].set_label('\'o\' Options on')
            else:
                self.dicHandles['Options'].set_label('\'o\' Options off')

        elif key == 'z':
            self.zoomStatus = set(['X','Y']).difference(set(self.zoomStatus)).pop()
            self.bzoom.label.set_text(self.zoomStatus + ' Zoom')
            self.fig.canvas.draw()
        elif key == 'x':
            self.zoomStatus = 'X'
            self.bzoom.label.set_text(self.zoomStatus + ' Zoom')
            self.fig.canvas.draw()
        elif key == 'y':
            self.zoomStatus = 'Y'
            self.bzoom.label.set_text(self.zoomStatus + ' Zoom')
            self.fig.canvas.draw()
        elif key == 'right':
            self.next(event)
        elif key == 'left':
            self.prev(event)
        elif key == 'up':
            self.zoom(event)
        elif key == 'down':
            self.zoom(event)
        elif key == 'h' or key == 'escape':
            self.home(event)

        self.ax.legend()
        self.fig.canvas.draw()

    def button_press(self, event):
        if event.button != 3:
            return
        if PickPoints.lock is not None:
            return
        self.initialPos = (event.xdata, event.ydata)
        PickPoints.lock = self

    def on_motion(self, event):
        if PickPoints.lock is not self:
            return
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        if event.xdata == None or event.ydata == None:
            return
        
        xdisplacement = event.xdata - self.initialPos[0]
        ydisplacement = event.ydata - self.initialPos[1]

        self.plotObject.plotData( cur_xlim[0] - xdisplacement,
                cur_xlim[1] - xdisplacement)
        self.ax.set_ylim([ cur_ylim[0] - ydisplacement,
            cur_ylim[1] - ydisplacement ])

        self.fig.canvas.draw()

    def button_release(self, event):
        if event.button != 3:
            return
        PickPoints.lock = None
        self.initialPos = None

        xlim = self.ax.get_xlim()
        Mean = (xlim[1] + xlim[0])/2.

        ClosestIndex = int(Mean / stepSize)
        self.ind = ClosestIndex

        self.fig.canvas.draw()

    # Based on https://gist.github.com/tacaswell/3144287
    def zoom(self, event, base_scale=1.5):
        # get the current x and y limits
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0])
        cur_yrange = (cur_ylim[1] - cur_ylim[0])
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location

        relposx = (xdata - cur_xlim[0]) / cur_xrange
        relposy = (ydata - cur_ylim[0]) / cur_yrange

        if isinstance(event, MouseEvent):
            button = event.button
        elif isinstance(event, KeyEvent):
            button = event.key
        else: #This should never happen!
            print 'ERROR'
            assert(False)

        if button == 'up':
            # deal with zoom in
            scale_factor = 1/base_scale
        elif button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print button
        # set new limits
        if self.zoomStatus == 'X':
            ylim = self.ax.get_ylim()
            self.plotObject.plotData( xdata - cur_xrange*scale_factor*relposx,
                    xdata + cur_xrange*scale_factor*(1-relposx) )
            self.ax.set_ylim(ylim)
        elif self.zoomStatus == 'Y':
            if cur_yrange > 2.5*self.plotObject.Mean:
                self.ax.set_ylim([ max(0,ydata - cur_yrange*scale_factor*relposy),
                    ydata + cur_yrange*scale_factor*(1-relposy)])
            else:
                self.ax.set_ylim([ ydata - cur_yrange*scale_factor*relposy,
                    ydata + cur_yrange*scale_factor*(1-relposy)])

        self.fig.canvas.draw() # force re-draw

    def click_zoom(self, event):
        self.zoomStatus = set(['X','Y']).difference(set(self.zoomStatus)).pop()
        self.bzoom.label.set_text(self.zoomStatus + ' Zoom')
        self.fig.canvas.draw()

    def update(self):
        self.plotObject.plotData( stepSize*self.ind, stepSize*self.ind+winSize )
        self.ax.set_ylim( self.ylim )
        self.ax.get_figure().canvas.draw()

    def prev(self, event):
        if self.ind > 0:
            self.ind -= 1
        else:
            self.ind = 0
        self.update()

    def next(self, event):
        if stepSize*(self.ind+1) < self.end:
            self.ind += 1
        self.update()

    def home(self, event):
        self.update()



class PlotData(QtGui.QDialog):
    DPI = 80

    def __init__(self, db, datafile, parent=None):
        QtGui.QWidget.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.graphIPI.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        self.ui.graphIPI.canvas.setFocus()

        self.dialogIPI = IPIWindow()

        self.resizeEvent = self.onResize
        self.showMaximized()

        self.fig = self.ui.graphIPI.canvas.fig
        self.ax = self.ui.graphIPI.canvas.ax
        self.ax.yaxis.grid()
        self.sigfig = self.ui.graphwave.canvas.fig
        self.sigaxes = self.ui.graphwave.canvas.sigaxes
        
        self.scatterFlag = True

        self.db = db
       
        # Loads on memory variables necessary for plotting
        # And dictionary from correctedSample to db off key
        # Runs the whole DB
        self.loadDataFromDB()
        
        self.SVM2Plot = []
        self.SVM2Plot.append( self.SVM[0].repeat(3) )
        self.SVM2Plot.append( self.SVM[1].repeat(3) )

        Min = -0.1
        Max = max( np.diff(self.TS[0]).max(), np.diff(self.TS[1]).max() )
        self.SVMY = np.array( self.Tam * [Min,Max,Min] )

        self.formatterX = FuncFormatter(self.sec2hms)
        self.formatterY = FuncFormatter(self.sec2msus)

        self.plotted = False
        self.plotData(0, winSize) # Creates self.fig and self.ui.graphIPI.canvas.ax.attributes
        self.createSigFig() # Creates self.sigfig, self.ui.graphwave.canvas.sigaxes attributes

        self.datafile = datafile
        self.TS = self.TS
        
    def __exit__(self):
        self.db.close()
        
    def loadDataFromDB(self):
        self.offsDic = {}
        self.correctedPosDic = {}
        
        P1 = []
        direction1 = []
        SVM1 = []
        probs1 = []
        dists1 = []
        
        P2 = []
        direction2 = []
        SVM2 = []
        probs2 = []
        dists2 = []
        
        for rec in self.db.iteritems():
            key, bindata = rec
            off, = struct.unpack('q',key)
            presentFish, direction, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB, spkdata = recogdb.parseDBHeader(bindata)
            
            if correctedPosA != -1:
                self.offsDic[correctedPosA] = off
                self.correctedPosDic[off] = correctedPosA
            if correctedPosB != -1:
                self.offsDic[correctedPosB] = off
                self.correctedPosDic[off] = correctedPosB
            
            assert ( (presentFish == 1) or (presentFish ==  2) or (presentFish == 3) )
            
            if presentFish == 1:
                P1.append(correctedPosA)
                direction1.append(direction)
                probs1.append( (probA, probB) )
                dists1.append( (distA, distB, distAB) )
                if svm == 's':
                    SVM1.append(correctedPosA)
                
            elif presentFish == 2:
                P2.append(correctedPosB)
                direction2.append(direction)
                probs2.append( (probA, probB) )
                dists2.append( (distA, distB, distAB) )
                if svm == 's':
                    SVM2.append(correctedPosB)
                
            else:
                P1.append(correctedPosA)
                direction1.append(direction)
                probs1.append( (probA, probB) )
                dists1.append( (distA, distB, distAB) )
                # 2 fish on same window is never a SVM classification
                
                P2.append(correctedPosB)
                direction2.append(direction)
                probs2.append( (probA,probB) )
                dists2.append( (distA, distB, distAB) )
                # 2 fish on same window is never a SVM classification
                
        
        self.TS = ( np.array(P1)/freq, np.array(P2)/freq )
        self.direction = ( np.array(direction1), np.array(direction2) )
        self.SVM = ( np.array(SVM1)/freq, np.array(SVM2)/freq )
        self.Tam = self.SVM[0].size
        self.probs = (probs1, probs2)
        self.dists = (dists1, dists2)
        

    def onResize(self,event):
        self.ui.formLayoutWidget.setGeometry(0,0,self.size().width(),self.size().height())

    def createSigFig(self):
        NColumns = self.ui.graphwave.canvas.NColumns

        for i in xrange(NChan):
            self.sigaxes[i].xaxis.set_major_formatter(self.formatterX)
            self.sigaxes[i].set_ylabel(u'$A_{%s}$ (V)'%i)
            self.sigaxes[i].xaxis.set_major_locator(plt.LinearLocator(numticks=5))
            self.sigaxes[i].yaxis.set_major_locator(plt.LinearLocator(numticks=3))
            self.sigaxes[i].grid()
            self.sigaxes[i].plot( [], [], 'k-')
        for ax in self.sigaxes[:-NColumns]:
            plt.setp(ax.get_xticklabels(), visible=False)
            plt.setp(ax.xaxis.get_offset_text(), visible=False)

        self.lines = []

    def plotSigData(self, central, spksurroudings=25*128):
        while len(self.lines) != 0:
            self.lines.pop().remove()

        centralts, color = central
        nextP1 = next(n for n,spk in enumerate(self.TS[0]) if spk >= centralts)
        surrP1 = self.TS[0][nextP1-10:nextP1+10]

        nextP2 = next(n for n,spk in enumerate(self.TS[1]) if spk >= centralts)
        surrP2 = self.TS[1][nextP2-10:nextP2+10]

        samples = int(round(centralts * freq)) - spksurroudings/2 # The timestamp is on the zero crossing
        f = self.datafile
        f.seek(samples*NChan*4)
        data = np.frombuffer(f.read(4*spksurroudings*NChan), dtype=np.float32)
        nsamples = data.size // NChan

        t = np.arange(samples, samples+nsamples) / freq

        ymax = max(data)
        ymin = min(data)
        ylim = max(abs(ymax),abs(ymin))
        for i in xrange(NChan):
            ax = self.sigaxes[i]
            ax.get_lines()[0].set_xdata(t)
            ax.get_lines()[0].set_ydata(data[i::NChan])
            ax.set_xlim( (t[0],t[-1]) )
            ax.set_ylim( (-ylim, ylim) )
            for ts in surrP1:
                self.lines.append(ax.axvline(ts, color='b',lw=2,alpha=0.4, picker=4))
            for ts in surrP2:
                self.lines.append(ax.axvline(ts, color='r',lw=2,alpha=0.4, picker=4))
            self.lines.append(ax.axvline(centralts,color=color,lw=2,alpha=1))
        
        self.sigfig.canvas.draw()

    def plotData(self, minX, maxX):

        L = maxX - minX
        MIN = minX
        MAX = maxX

        try:
            minIdxX1 = next( n for n,i in enumerate(self.TS[0]) if i > MIN )
        except StopIteration:
            minIdxX1 = self.TS[0].size-1
        try:
            minIdxX2 = next( n for n,i in enumerate(self.TS[1]) if i > MIN )
        except StopIteration:
            minIdxX2 = self.TS[1].size-1

        try:
            maxIdxX1 = next( n for n,i in enumerate(self.TS[0]) if i > MAX)
        except StopIteration:
            maxIdxX1 = self.TS[0].size-1
        try:
            maxIdxX2 = next( n for n,i in enumerate(self.TS[1]) if i > MAX)+1
        except StopIteration:
            maxIdxX2 = self.TS[1].size-1

        # Only plot once
        if self.plotted == False:
            # Plot SVM Lines
            self.ax.plot(self.SVM2Plot[0], self.SVMY, 'b-.', alpha=0.3, lw=2)
            self.ax.plot(self.SVM2Plot[1], self.SVMY, 'r-.', alpha=0.3, lw=2)

            # Lines and dots are plotter separately for picker act only on dots
            self.ax.plot(self.TS[1][1:], np.diff(self.TS[1]), 'r-')
            self.ax.plot(self.TS[0][1:], np.diff(self.TS[0]), 'b-')
            
            self.plotted = True
        
        try:
            self.scatter1d.remove()
        except:
            pass
        try:
            self.scatter2d.remove()
        except:
            pass
        try:
            self.scatter1r.remove()
        except:
            pass
        try:
            self.scatter2r.remove()
        except:
            pass
        try:
            self.scatter1s.remove()
        except:
            pass
        try:
            self.scatter2s.remove()
        except:
            pass
        try:
            self.plot1.pop(0).remove()
        except:
            pass
        try:
            self.plot2.pop(0).remove()
        except:
            pass

        # Color proportional to probability only if window is lesser than 30s
        if L<=30 and self.scatterFlag == True:
            self.isScatter = True

            P0 = [i for i,j in self.probs[0][minIdxX1:maxIdxX1]]
            P1 = [j for i,j in self.probs[1][minIdxX2:maxIdxX2]]

            color1 = [ num2color(int(255*i),'b') for i in P0[1:] ]
            color2 = [ num2color(int(255*i),'r') for i in P1[1:] ]

            size1 = 1*np.array([ min(self.dists[0][i]) for i in xrange(minIdxX1,maxIdxX1-1) ])
            size2 = 1*np.array([ min(self.dists[1][i]) for i in xrange(minIdxX2,maxIdxX2-1) ])

            directIdx1 = find(self.direction[0][minIdxX1:maxIdxX1][1:] > 0)
            directIdx2 = find(self.direction[1][minIdxX2:maxIdxX2][1:] > 0)

            self.scatter1d = self.ax.scatter(self.TS[0][minIdxX1:maxIdxX1][1:][directIdx1], np.diff(self.TS[0][minIdxX1:maxIdxX1])[directIdx1], c=color1, marker='>', linewidths=0, s=50+np.pi*size1, picker=3, zorder=IPIDATABLUE)
            self.scatter2d = self.ax.scatter(self.TS[1][minIdxX2:maxIdxX2][1:][directIdx2], np.diff(self.TS[1][minIdxX2:maxIdxX2])[directIdx2], c=color2, marker='>', linewidths=0, s=50+np.pi*size2, picker=3, zorder=IPIDATARED)

            reverseIdx1 = find(self.direction[0][minIdxX1:maxIdxX1][1:] < 0)
            reverseIdx2 = find(self.direction[1][minIdxX2:maxIdxX2][1:] < 0)

            self.scatter1r = self.ax.scatter(self.TS[0][minIdxX1:maxIdxX1][1:][reverseIdx1], np.diff(self.TS[0][minIdxX1:maxIdxX1])[reverseIdx1], c=color1, marker='<', linewidths=0, s=50+np.pi*size1, picker=3, zorder=IPIDATABLUE)
            self.scatter2r = self.ax.scatter(self.TS[1][minIdxX2:maxIdxX2][1:][reverseIdx2], np.diff(self.TS[1][minIdxX2:maxIdxX2])[reverseIdx2], c=color2, marker='<', linewidths=0, s=50+np.pi*size2, picker=3, zorder=IPIDATARED)

            svmIdx1 = find(self.direction[0][minIdxX1:maxIdxX1][1:] == 0)
            svmIdx2 = find(self.direction[1][minIdxX2:maxIdxX2][1:] == 0)

            self.scatter1s = self.ax.scatter(self.TS[0][minIdxX1:maxIdxX1][1:][svmIdx1], np.diff(self.TS[0][minIdxX1:maxIdxX1])[svmIdx1], c=color1, marker='o', linewidths=0, s=20+np.pi*size1, picker=3, zorder=IPIDATABLUE)
            self.scatter2s = self.ax.scatter(self.TS[1][minIdxX2:maxIdxX2][1:][svmIdx2], np.diff(self.TS[1][minIdxX2:maxIdxX2])[svmIdx2], c=color2, marker='o', linewidths=0, s=20+np.pi*size2, picker=3, zorder=IPIDATARED)

        else:
            self.isScatter = False

            self.plot1 = self.ax.plot(self.TS[0][minIdxX1:maxIdxX1][1:], np.diff(self.TS[0][minIdxX1:maxIdxX1]), 'b.', mew=2, picker=5, zorder=IPIDATABLUE)
            self.plot2 = self.ax.plot(self.TS[1][minIdxX2:maxIdxX2][1:], np.diff(self.TS[1][minIdxX2:maxIdxX2]), 'r.', mew=2, picker=5, zorder=IPIDATARED)

        self.adjustAxes(minX, maxX)

    def adjustAxes(self, minX, maxX):
        self.ax.set_title('IPIs and SVM classification')
        self.ax.xaxis.set_major_formatter(self.formatterX)
        self.ax.yaxis.set_major_formatter(self.formatterY)

        self.Mean = ( np.diff(self.TS[0]).mean() + np.diff(self.TS[1]).mean() ) / 2.
        YMIN = 0.
        YMAX = 2.5 * self.Mean

        self.ax.axis([minX, maxX, YMIN, YMAX])

    def sec2hms(self, x, pos):
        t = int(round(1e4*x))
        s, ms = divmod(t, 1e4)
        m, s = divmod(x, 60)
        h, m = divmod(m, 60)
        return '%02d:%02d:%02d.%04d' % (h, m, s, ms)

    def sec2msus(self,x,pos):
        ms = int(1e3*x)
        us = int(((1e3*x)%1)*1e3)
        return '%03d.%03d' % (ms,us)


if __name__ == '__main__':
    description = 'Browse the IPI of the generated time series and provides tools for manual correction'
    parser = MyParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('db_file', type=str, help='Databank generated file')
    parser.add_argument('timeseries_file', type=file, help='Location of the timeseries (I32) file')
    parser.add_argument('--stepSize', type=float, default=90., help='Step size for moving on the IPI time series. Default = 90s')
    parser.add_argument('--winSize', type=float, default=120., help='Window size for plotting the IPI time series. Default = 120s')

    args = parser.parse_args()
    dbf = args.db_file
    datafile = args.timeseries_file
    stepSize = args.stepSize
    winSize = args.winSize

    if os.path.isfile(dbf) == False:
        print 'DB file not found'

    app = QtGui.QApplication(sys.argv)

    db = recogdb.openDB(dbf,'r')

    myapp = PlotData(db, datafile)

    Pick = PickPoints(myapp)

    myapp.show()
    sys.exit(app.exec_())
