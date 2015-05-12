from PyQt4 import QtCore, QtGui
from single2overlapInterface import *

import numpy as np

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
    
spkSize = 128
freq = 45454.54545454
saturationLow = -10
saturationHigh = 10
dicFields = {'presentFish': 0,
        'direction': 1,
        'distA': 2,
        'distB': 3,
        'distAB': 4,
        'flags': 5,
        'correctedPosA': 6,
        'correctedPosB': 7,
        'svm': 8,
        'pairsvm': 9,
        'probA': 10,
        'probB': 11,
}
    
class single2overlap(QtGui.QDialog):
    
    def __init__(self, NChan, datafile):
        QtGui.QWidget.__init__(self)
        self.uiObject = Ui_single2overlap()
        self.uiObject.setupUi(self)
        
        self.resizeEvent = self.onResize
        self.setWindowState(QtCore.Qt.WindowMaximized)
        
        self.datafile = datafile
        
        self.uiObject.fishAButton.setChecked(True)
        
        self.curChan = 0
        
        self.uiObject.channelSelector.setMaximum(NChan-1)
        self.uiObject.channelNumber.setText(_translate("single2overlap", str(self.curChan), None))
        
        QtCore.QObject.connect(self.uiObject.cancelButton, QtCore.SIGNAL('clicked()'), self.close)
        QtCore.QObject.connect(self.uiObject.okButton, QtCore.SIGNAL('clicked()'), self.okClick)
        QtCore.QObject.connect(self.uiObject.channelSelector, QtCore.SIGNAL('valueChanged(int)'), self.movingChannels)

        self.NChan = NChan
        self.replot = False
        
        self.move(0,0)
        
        self.axPrev1 = self.uiObject.prev1.canvas.ax
        self.axPrev2 = self.uiObject.prev2.canvas.ax
        self.axSpike = self.uiObject.spike.canvas.ax
        self.axNext1 = self.uiObject.next1.canvas.ax
        self.axNext2 = self.uiObject.next2.canvas.ax
        
        self.positionSelectorClick = self.uiObject.spike.canvas.fig.canvas.mpl_connect('button_press_event', self.spikeClick)
        self.positionSelectorMove = self.uiObject.spike.canvas.fig.canvas.mpl_connect('motion_notify_event', self.spikeMove)
        self.positionSelectorRelease = self.uiObject.spike.canvas.fig.canvas.mpl_connect('button_release_event', self.spikeRelease)
        
        self.createFigures()
        
        self.posA = None
        self.posB = None
    
    def onResize(self,event):
        self.uiObject.mainLayout.setGeometry( QtCore.QRect(0,0,self.size().width(),self.size().height()) )
    
    def okClick(self):
        if (self.posA == None) or (self.posB == None):
            QtGui.QMessageBox.warning(self, "Warning", \
                              "Please, select the instant of occurrence of both fish.", \
                              QtGui.QMessageBox.Cancel, \
                              QtGui.QMessageBox.NoButton, \
                              QtGui.QMessageBox.NoButton)
        else:
            self.replot = True
            self.close()
    
    def spikeClick(self,event):
        pos = 1000*np.round((event.xdata/1000.)*freq) / freq
        self.drawSpikePos(pos)
    
    def spikeMove(self,event):
        if event.button == 1:
            pos = 1000*np.round((event.xdata/1000.)*freq) / freq
            self.drawSpikePos(pos)
    
    def spikeRelease(self,event):
        pos = 1000*np.round((event.xdata/1000.)*freq) / freq
        self.drawSpikePos(pos)
        if self.uiObject.fishAButton.isChecked() == True:
            # correctedPos -> position in SAMPLES from the beginning of the file
            correctedPos = pos*freq/1000. + self.off_now/4/self.NChan
            self.posA = int(np.round(correctedPos))
            self.uiObject.fishBButton.setChecked(True)
        elif self.uiObject.fishBButton.isChecked() == True:
            # correctedPos -> position in SAMPLES from the beginning of the file
            correctedPos = pos*freq/1000. + self.off_now/4/self.NChan
            self.posB = int(np.round(correctedPos))
            self.uiObject.fishAButton.setChecked(True)
        
    
    def drawSpikePos(self, pos):
        if self.uiObject.fishAButton.isChecked() == True:
            color = 'b'
        elif self.uiObject.fishBButton.isChecked() == True:
            color = 'r'
        else:
            assert False
        
        Ylim = (saturationLow, saturationHigh)
        self.lineDic[color].set_xdata( (pos, pos) )
        self.lineDic[color].set_ydata( Ylim )
        self.uiObject.spike.canvas.fig.canvas.draw()

    def movingChannels(self, position):
        self.uiObject.channelNumber.setText(_translate("single2overlap", str(position), None))
        self.replotSignals(position)
    
    def createFigures(self):
        self.axPrev1.set_title('Previous fish A EOD')
        self.plotPrev1, = self.axPrev1.plot( [], [], 'b.-')
        
        self.axPrev2.set_title('Previous fish B EOD')
        self.plotPrev2, = self.axPrev2.plot( [], [], 'r.-')
        
        self.axSpike.set_title('Selected EOD to convert to overlapping spike')
        self.plotSpike, = self.axSpike.plot( [], [], 'k.-')
        lineSpikePosB, = self.axSpike.plot( [], [], 'b-')
        lineSpikePosR, = self.axSpike.plot( [], [], 'r-')
        self.lineDic = {'b': lineSpikePosB, \
                        'r': lineSpikePosR, \
                        }
        
        self.axNext1.set_title('Next fish A EOD')
        self.plotNext1, = self.axNext1.plot( [], [], 'b.-')
        
        self.axNext2.set_title('Next fish B EOD')
        self.plotNext2, = self.axNext2.plot( [], [], 'r.-')
    
    def plotSignals(self, data, channel=0):
        f = self.datafile
        
        self.off_pB, entry_pB = data[0]
        self.off_pR, entry_pR = data[1]
        self.off_now, entry_now = data[2]
        self.off_nB, entry_nB = data[3]
        self.off_nR, entry_nR = data[4]
        
        correctedPos_pB = entry_pB[ dicFields['correctedPosA'] ]
        correctedPos_pR = entry_pR[ dicFields['correctedPosB'] ]
        correctedPos_nowB = entry_now[ dicFields['correctedPosA'] ]
        correctedPos_nowR = entry_now[ dicFields['correctedPosB'] ]
        correctedPos_nB = entry_nB[ dicFields['correctedPosA'] ]
        correctedPos_nR = entry_nR[ dicFields['correctedPosB'] ]
        
        # 1000 is to plot in ms
        sample2plot_pB = 1000.*(correctedPos_pB - self.off_pB/self.NChan/4.) / freq
        sample2plot_pR = 1000.*(correctedPos_pR - self.off_pR/self.NChan/4.) / freq
        sample2plot_nowB = 1000.*(correctedPos_nowB - self.off_now/self.NChan/4.) / freq
        sample2plot_nowR = 1000.*(correctedPos_nowR - self.off_now/self.NChan/4.) / freq
        sample2plot_nB = 1000.*(correctedPos_nB - self.off_nB/self.NChan/4.) / freq
        sample2plot_nR = 1000.*(correctedPos_nR - self.off_nR/self.NChan/4.) / freq
        
        t = 1000. * np.arange(spkSize) / freq
        
        # Previous blue plot
        f.seek(self.off_pB)
        self.data_pB = np.frombuffer(f.read(4*spkSize*self.NChan), dtype=np.float32)
        
        self.axPrev1.plot( (t.min(), t.max()), [0., 0.], 'k-.' )
        self.axPrev1.plot( (sample2plot_pB, sample2plot_pB), (saturationLow, saturationHigh), 'b-')
        self.plotPrev1.set_xdata(t)
        self.plotPrev1.set_ydata(self.data_pB[channel::self.NChan])
        
        self.axPrev1.set_xlim( (t.min(), t.max()) )

        # Previous red plot
        f.seek(self.off_pR)
        self.data_pR = np.frombuffer(f.read(4*spkSize*self.NChan), dtype=np.float32)
        
        self.axPrev2.plot( (t.min(), t.max()), [0., 0.], 'k-.' )
        self.axPrev2.plot( (sample2plot_pR, sample2plot_pR), (saturationLow, saturationHigh), 'r-')
        self.plotPrev2.set_xdata(t)
        self.plotPrev2.set_ydata(self.data_pR[channel::self.NChan])
        
        self.axPrev2.set_xlim( (t.min(), t.max()) )

        # Selected spike plot
        f.seek(self.off_now)
        self.data_now = np.frombuffer(f.read(4*spkSize*self.NChan), dtype=np.float32)
        
        self.axSpike.plot( (t.min(), t.max()), [0., 0.], 'k-.' )
        self.axSpike.plot( (sample2plot_nowB, sample2plot_nowB), (saturationLow, saturationHigh), 'k-.')
        self.axSpike.plot( (sample2plot_nowR, sample2plot_nowR), (saturationLow, saturationHigh), 'k-.')
        self.plotSpike.set_xdata(t)
        self.plotSpike.set_ydata(self.data_now[channel::self.NChan])
        
        self.axSpike.set_xlim( (t.min(), t.max()) )

        # Next blue plot
        f.seek(self.off_nB)
        self.data_nB = np.frombuffer(f.read(4*spkSize*self.NChan), dtype=np.float32)
        
        self.axNext1.plot( (t.min(), t.max()), [0., 0.], 'k-.' )
        self.axNext1.plot( (sample2plot_nB, sample2plot_nB), (saturationLow, saturationHigh), 'b-')
        self.plotNext1.set_xdata(t)
        self.plotNext1.set_ydata(self.data_nB[channel::self.NChan])
        
        self.axNext1.set_xlim( (t.min(), t.max()) )

        # Next red plot
        f.seek(self.off_nR)
        self.data_nR = np.frombuffer(f.read(4*spkSize*self.NChan), dtype=np.float32)
        
        self.axNext2.plot( (t.min(), t.max()), [0., 0.], 'k-.' )
        self.axNext2.plot( (sample2plot_nR, sample2plot_nR), (saturationLow, saturationHigh), 'r-')
        self.plotNext2.set_xdata(t)
        self.plotNext2.set_ydata(self.data_nR[channel::self.NChan])
        
        self.axNext2.set_xlim( (t.min(), t.max()) )

        self.adjustYLim(channel)
        self.drawAll()

        
    def adjustYLim(self, channel):
        minY = self.data_now[channel::self.NChan].min()
        maxY = self.data_now[channel::self.NChan].max()

        self.axPrev1.set_ylim( (maxY, minY ) )
        self.axPrev2.set_ylim( (maxY, minY ) )
        self.axSpike.set_ylim( (maxY, minY ) )
        self.axNext1.set_ylim( (maxY, minY ) )
        self.axNext2.set_ylim( (maxY, minY ) )
        
    def drawAll(self):    
        self.uiObject.prev1.canvas.fig.canvas.draw()
        self.uiObject.prev2.canvas.fig.canvas.draw()
        self.uiObject.spike.canvas.fig.canvas.draw()
        self.uiObject.next1.canvas.fig.canvas.draw()
        self.uiObject.next2.canvas.fig.canvas.draw()
        
    def replotSignals(self, channel):
        self.plotPrev1.set_ydata(self.data_pB[channel::self.NChan])
        self.plotPrev2.set_ydata(self.data_pR[channel::self.NChan])
        self.plotSpike.set_ydata(self.data_now[channel::self.NChan])
        self.plotNext1.set_ydata(self.data_nB[channel::self.NChan])
        self.plotNext2.set_ydata(self.data_nR[channel::self.NChan])
        
        self.adjustYLim(channel)
        self.drawAll()
