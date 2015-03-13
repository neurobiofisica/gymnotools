import numpy as np

import matplotlib ############################
import matplotlib.pyplot as plt
from matplotlib.mlab import find
from matplotlib.ticker import FuncFormatter
from matplotlib.widgets import Button
from matplotlib.backend_bases import MouseEvent, KeyEvent

import argparse
import sys
import time

from graphicalInterface import *

# Defines
SVMDATABLUE = 0
SVMDATARED = 1
IPIDATABLUE = 2
IPIDATARED = 3
LEGENDSVM = 4
LEGENDIPI = 5
LEGENDBLUE = 6
LEGENDRED = 7

FIGIPI = 1
FIGSIG = 2

# Constants
freq = 45454.545454
NChan = 11

###### Auxiliary funcs ####

# Auxiliary function for reading
def parseSVMFlags(f, col=3):
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
        self.ax.plot([], 'k-.', lw=2, label='\'s\' SVM off', zorder=LEGENDSVM)
        self.ax.plot([], 'k-', lw=2, label='\'i\' IPI off', zorder=LEGENDIPI)
        self.ax.plot([], 'b.-', mew=2, label='\'b\' Blue off', zorder=LEGENDBLUE)
        self.ax.plot([], 'r.-', mew=2, label='\'r\' Red off', zorder=LEGENDRED)
        self.ax.legend()
        handles, labels = self.ax.get_legend_handles_labels()

        self.cidpick = self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.cidpress = self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.cidzoom = self.fig.canvas.mpl_connect('scroll_event', self.zoom)
        self.cidbpress = self.fig.canvas.mpl_connect('button_press_event', self.button_press)
        self.cidmotion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cidbrelease = self.fig.canvas.mpl_connect('button_release_event', self.button_release)

        self.b = False
        self.r = False
        self.svm = False
        self.ipi = False

        self.initialPos = None


        self.dicHandles = {}

        for h in handles:
            if h.zorder == LEGENDBLUE:
                self.dicHandles.update( {'b':h} )
            elif h.zorder == LEGENDRED:
                self.dicHandles.update( {'r':h} )
            elif h.zorder == LEGENDIPI:
                self.dicHandles.update( {'IPI':h} )
            elif h.zorder == LEGENDSVM:
                self.dicHandles.update( {'SVM':h} )

        self.callback = self.Index(self.ax)
        self.make_buttons(self.callback)

    def make_buttons(self, callback):
        self.fig.subplots_adjust(bottom=0.15)

        axprev = self.fig.add_axes([0.001, 0.005, 0.1, 0.07])
        axhome = self.fig.add_axes([0.111, 0.005, 0.1, 0.07])
        axnext = self.fig.add_axes([0.221, 0.005, 0.1, 0.07])
        self.bnext = Button(axnext, 'Next')
        self.bnext.on_clicked(self.callback.next)
        self.bprev = Button(axprev, 'Previous')
        self.bprev.on_clicked(self.callback.prev)
        self.bhome = Button(axhome, 'Home')
        self.bhome.on_clicked(self.callback.home)

        self.fig.canvas.draw()

    def onpick(self,event):
        if event.mouseevent.button != 1:
            return
        zorder = event.artist.zorder
        if self.svm == True:
            if zorder == SVMDATABLUE and self.b == True:
                print (event.ind[0] / 3) + 1
                print (event.artist.get_xdata()[event.ind] * freq * 4 * NChan)[0]
            if zorder == SVMDATARED and self.r == True:
                print (event.ind[0] / 3) + 1
                print (event.artist.get_xdata()[event.ind] * freq * 4 * NChan)[0]
        if self.ipi == True and (\
                (zorder == IPIDATABLUE and self.b == True) or \
                (zorder == IPIDATARED and self.r == True)):
            if zorder == IPIDATABLUE:
                color = 'b'
            elif zorder == IPIDATARED:
                color = 'r'
            ind = event.ind[0]
            xdata = event.artist.get_xdata()
            central = (xdata[ind], color)
            self.plotObject.plotSigData(central)

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
        elif key == 'right':
            self.callback.next(event)
        elif key == 'left':
            self.callback.prev(event)
        elif key == 'up':
            self.zoom(event)
        elif key == 'down':
            self.zoom(event)
        elif key == 'h' or key == 'escape':
            self.callback.home(event)

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

        self.ax.set_xlim([ cur_xlim[0] - xdisplacement,
            cur_xlim[1] - xdisplacement ])
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
        self.callback.ind = ClosestIndex

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
        self.ax.set_xlim([xdata - cur_xrange*scale_factor*relposx,
                     xdata + cur_xrange*scale_factor*(1-relposx)])
        self.fig.canvas.draw() # force re-draw

    class Index:
        def __init__(self,ax):
            self.ind = 0
            self.ax = ax
            self.ylim = ax.get_ylim()
            self.end = ax.get_xaxis().get_data_interval()[1]

        def update(self):
            self.ax.set_xlim( (stepSize*self.ind, stepSize*self.ind+winSize) )
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

    def __init__(self, TS, SVMFlags, datafile, parent=None):
        QtGui.QWidget.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.graphIPI.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        self.ui.graphIPI.canvas.setFocus()

        self.resizeEvent = self.onResize
        self.showMaximized()

        self.fig = self.ui.graphIPI.canvas.fig
        self.ax = self.ui.graphIPI.canvas.ax
        self.sigfig = self.ui.graphwave.canvas.fig
        self.sigaxes = self.ui.graphwave.canvas.sigaxes

        IdxP1 = find(TS[0] == 1)
        IdxP2 = find(TS[0] == -1)

        P1 = TS[1][ IdxP1 ] / freq
        P2 = TS[1][ IdxP2 ] / freq

        self.TS = (P1, P2)

        self.SVM = TS[1][ find(SVMFlags == 's') ]
        self.Tam = self.SVM[0].size

        svmFlag1 = SVMFlags[ IdxP1 ]
        svmFlag2 = SVMFlags[ IdxP2 ]
        self.svmFlags = (svmFlag1, svmFlag2)

        ProbP1 = TS[3][ IdxP1 ]
        ProbP2 = TS[4][ IdxP2 ]

        self.probs = (ProbP1, ProbP2)

        distP1 = ( TS[5][ IdxP1 ], TS[6][ IdxP1 ], TS[7][ IdxP1 ] )
        distP2 = ( TS[5][ IdxP2 ], TS[6][ IdxP2 ], TS[7][ IdxP2 ] )

        self.dists = (distP1, distP2)

        self.SVM2Plot = []
        self.SVM2Plot.append( self.SVM[0].repeat(3) )
        self.SVM2Plot.append( self.SVM[1].repeat(3) )

        Min = -0.1
        Max = max( np.diff(self.TS[0]).max(), np.diff(self.TS[1]).max() )
        self.SVMY = np.array( self.Tam * [Min,Max,Min] )

        self.formatter = FuncFormatter(self.sec2hms)

        self.plotData() # Creates self.fig and self.ui.graphIPI.canvas.ax.attributes
        self.createSigFig() # Creates self.sigfig, self.ui.graphwave.canvas.sigaxes attributes

        self.datafile = datafile
        self.TS = self.TS

    def onResize(self,event):
        self.ui.formLayoutWidget.setGeometry(0,0,self.size().width(),self.size().height())
        #self.ui.graphwave.setGeometry(0,0,self.size().width(),450)

    def createSigFig(self):
        NColumns = self.ui.graphwave.canvas.NColumns
        #NRows = NChan/NColumns + NChan%NColumns
        #self.sigfig = plt.figure(FIGSIG, figsize=(NColumns*(700./self.DPI),900./self.DPI/NColumns), dpi=self.DPI)
        #self.ui.graphwave.canvas.sigaxes = [self.sigfig.add_subplot(NRows,NColumns,1)] #2 columns
        #self.ui.graphwave.canvas.sigaxes += [self.sigfig.add_subplot(NRows,NColumns,i, \
        #        sharex=self.ui.graphwave.canvas.sigaxes[0], sharey=self.ui.graphwave.canvas.sigaxes[0]) \
        #        for i in xrange(2,NChan+1)]
        #self.sigfig.subplots_adjust(hspace=0.20) #################

        for i in xrange(NChan):
            self.sigaxes[i].xaxis.set_major_formatter(self.formatter)
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

    def plotData(self):
        #self.fig = plt.figure(FIGIPI, figsize=(700./self.DPI,450./self.DPI), dpi=self.DPI)
        #self.ax= self.fig.add_subplot(1,1,1)

        self.ax.plot(self.SVM2Plot[0], self.SVMY, 'b-.', alpha=0.3, lw=2, picker=5, zorder=SVMDATABLUE)
        self.ax.plot(self.SVM2Plot[1], self.SVMY, 'r-.', alpha=0.3, lw=2, picker=5, zorder=SVMDATARED)

        # Lines and dots are plotter separately for picker act only on dots
        self.ax.plot(self.TS[0][:-1], np.diff(self.TS[0]), 'b-')
        self.ax.plot(self.TS[1][:-1], np.diff(self.TS[1]), 'r-')

        self.ax.plot(self.TS[0][:-1], np.diff(self.TS[0]), 'b.', mew=2, picker=5, zorder=IPIDATABLUE)
        self.ax.plot(self.TS[1][:-1], np.diff(self.TS[1]), 'r.', mew=2, picker=5, zorder=IPIDATARED)

        self.adjustAxes()

    def adjustAxes(self):
        self.ax.set_title('IPIs and SVM classification')
        self.ax.xaxis.set_major_formatter(self.formatter)

        Mean = ( np.diff(self.TS[0]).mean() + np.diff(self.TS[1]).mean() ) / 2.
        YMIN = 0.
        YMAX = 2.5 * Mean

        self.ax.axis([0, winSize, YMIN, YMAX])

    def sec2hms(self, x, pos):
        t = int(round(1e4*x))
        s, ms = divmod(t, 1e4)
        m, s = divmod(x, 60)
        h, m = divmod(m, 60)
        return '%02d:%02d:%02d.%04d' % (h, m, s, ms)



if __name__ == '__main__':
    description = 'Browse the IPI of the generated time series and provides tools for manual correction'
    parser = MyParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('timestamps_file', type=file, help='Location of the timestamps generated file')
    parser.add_argument('timeseries_file', type=file, help='Location of the timeseries (I32) file')
    parser.add_argument('--stepSize', type=float, default=90., help='Step size for moving on the IPI time series. Default = 90s')
    parser.add_argument('--winSize', type=float, default=120., help='Window size for plotting the IPI time series. Default = 120s')

    args = parser.parse_args()
    timestampsf = args.timestamps_file
    datafile = args.timeseries_file
    stepSize = args.stepSize
    winSize = args.winSize

    app = QtGui.QApplication(sys.argv)

    TS = np.loadtxt(timestampsf,unpack=True,usecols=(0,1,2,4,5,6,7,8))
    timestampsf.seek(0)
    svmFlags = np.array(parseSVMFlags(timestampsf))
    timestampsf.close()

    myapp = PlotData(TS, svmFlags, datafile)

    Pick = PickPoints(myapp)

    myapp.show()
    sys.exit(app.exec_())
