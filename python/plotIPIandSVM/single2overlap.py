from PyQt4 import QtCore, QtGui
from single2overlapInterface import *

import sys, os
if os.getcwd().split('/')[-1] == 'gui':
    sys.path.append( os.path.realpath('../python') )
elif os.getcwd().split('/')[-1] == 'plotIPIandSVM':
    sys.path.append( os.path.realpath('../') )
import recogdb

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
    
class single2overlap(QtGui.QDialog):
    
    def __init__(self, db, NChan, datafile):
        QtGui.QWidget.__init__(self)
        self.uiObject = Ui_single2overlap()
        self.uiObject.setupUi(self)
        
        self.resizeEvent = self.onResize
        self.setWindowState(QtCore.Qt.WindowMaximized)
        
        self.db = db
        
        self.datafile = datafile
        
        self.uiObject.fishAButton.setChecked(True)
        
        self.curChan = 0
        
        self.uiObject.channelSelector.setMaximum(NChan-1)
        self.uiObject.channelNumber.setText(_translate("single2overlap", str(self.curChan), None))
        
        QtCore.QObject.connect(self.uiObject.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)
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
        
        self.zLine_pB = []
        self.cLine_pB = []
        self.zLine_pR = []
        self.cLine_pR = []
        
        self.zLine_Spk = []
        self.cLine_SpkB = []
        self.cLine_SpkR = []
        
        self.zLine_nB = []
        self.cLine_nB = []
        self.zLine_nR = []
        self.cLine_nR = []
        
        self.positionSelectorClick = self.uiObject.spike.canvas.fig.canvas.mpl_connect('button_press_event', self.spikeClick)
        self.positionSelectorMove = self.uiObject.spike.canvas.fig.canvas.mpl_connect('motion_notify_event', self.spikeMove)
        self.positionSelectorRelease = self.uiObject.spike.canvas.fig.canvas.mpl_connect('button_release_event', self.spikeRelease)
        
        self.createFigures()
        
        self.posA = None
        self.posB = None
    
    def cancel(self):
        self.posA = None
        self.posB = None
        self.close()
    
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
        # Remove old lines
        while len(self.zLine_pB) > 0:
            self.zLine_pB.pop().remove()
        while len(self.cLine_pB) > 0:
            self.cLine_pB.pop().remove()
        while len(self.zLine_pR) > 0:
            self.zLine_pR.pop().remove()
        while len(self.cLine_pR) > 0:
            self.cLine_pR.pop().remove()
            
        while len(self.zLine_Spk) > 0:
            self.zLine_Spk.pop().remove()
        while len(self.cLine_SpkB) > 0:
            self.cLine_SpkB.pop().remove()
        while len(self.cLine_SpkR) > 0:
            self.cLine_SpkR.pop().remove()
        
        while len(self.zLine_nB) > 0:
            self.zLine_nB.pop().remove()
        while len(self.cLine_nB) > 0:
            self.cLine_nB.pop().remove()
        while len(self.zLine_nR) > 0:
            self.zLine_nR.pop().remove()
        while len(self.cLine_nR) > 0:
            self.cLine_nR.pop().remove()
        
        f = self.datafile
        
        self.off_pB, entry_pB = data[0]
        self.off_pR, entry_pR = data[1]
        self.off_now, entry_now = data[2]
        self.off_nB, entry_nB = data[3]
        self.off_nR, entry_nR = data[4]
        
        NSamples_pB = recogdb.getNSamples(self.db, self.off_pB)
        NSamples_pR = recogdb.getNSamples(self.db, self.off_pR)
        NSamples_now = recogdb.getNSamples(self.db, self.off_now)
        NSamples_nB = recogdb.getNSamples(self.db, self.off_nB)
        NSamples_nR = recogdb.getNSamples(self.db, self.off_nR)
        
        correctedPos_pB = entry_pB[ recogdb.dicFields['correctedPosA'] ]
        correctedPos_pR = entry_pR[ recogdb.dicFields['correctedPosB'] ]
        correctedPos_nowB = entry_now[ recogdb.dicFields['correctedPosA'] ]
        correctedPos_nowR = entry_now[ recogdb.dicFields['correctedPosB'] ]
        correctedPos_nB = entry_nB[ recogdb.dicFields['correctedPosA'] ]
        correctedPos_nR = entry_nR[ recogdb.dicFields['correctedPosB'] ]
        
        # 1000 is to plot in ms
        sample2plot_pB = 1000.*(correctedPos_pB - self.off_pB/self.NChan/4.) / freq
        sample2plot_pR = 1000.*(correctedPos_pR - self.off_pR/self.NChan/4.) / freq
        sample2plot_nowB = 1000.*(correctedPos_nowB - self.off_now/self.NChan/4.) / freq
        sample2plot_nowR = 1000.*(correctedPos_nowR - self.off_now/self.NChan/4.) / freq
        sample2plot_nB = 1000.*(correctedPos_nB - self.off_nB/self.NChan/4.) / freq
        sample2plot_nR = 1000.*(correctedPos_nR - self.off_nR/self.NChan/4.) / freq
        
        t_pB = 1000. * np.arange(NSamples_pB) / freq
        t_pR = 1000. * np.arange(NSamples_pR) / freq
        t_now = 1000. * np.arange(NSamples_now) / freq
        t_nB = 1000. * np.arange(NSamples_nB) / freq
        t_nR = 1000. * np.arange(NSamples_nR) / freq
        
        # Previous blue plot
        
        f.seek(self.off_pB)
        self.data_pB = np.frombuffer(f.read(4*NSamples_pB*self.NChan), dtype=np.float32)
        
        self.zLine_pB = self.axPrev1.plot( (t_pB.min(), t_pB.max()), [0., 0.], 'k-.' )
        self.cLine_pB = self.axPrev1.plot( (sample2plot_pB, sample2plot_pB), (saturationLow, saturationHigh), 'b-')
        self.plotPrev1.set_xdata(t_pB)
        self.plotPrev1.set_ydata(self.data_pB[channel::self.NChan])
        
        self.axPrev1.set_xlim( (t_pB.min(), t_pB.max()) )

        # Previous red plot
        
        f.seek(self.off_pR)
        self.data_pR = np.frombuffer(f.read(4*NSamples_pR*self.NChan), dtype=np.float32)
        
        self.zLine_pR = self.axPrev2.plot( (t_pR.min(), t_pR.max()), [0., 0.], 'k-.' )
        self.cLine_pR = self.axPrev2.plot( (sample2plot_pR, sample2plot_pR), (saturationLow, saturationHigh), 'r-')
        self.plotPrev2.set_xdata(t_pR)
        self.plotPrev2.set_ydata(self.data_pR[channel::self.NChan])
        
        self.axPrev2.set_xlim( (t_pR.min(), t_pR.max()) )

        # Selected spike plot
        
        f.seek(self.off_now)
        self.data_now = np.frombuffer(f.read(4*NSamples_now*self.NChan), dtype=np.float32)
        
        self.zLine_Spk = self.axSpike.plot( (t_now.min(), t_now.max()), [0., 0.], 'k-.' )
        self.cLine_SpkB = self.axSpike.plot( (sample2plot_nowB, sample2plot_nowB), (saturationLow, saturationHigh), 'k-.')
        self.cLine_SpkR = self.axSpike.plot( (sample2plot_nowR, sample2plot_nowR), (saturationLow, saturationHigh), 'k-.')
        self.plotSpike.set_xdata(t_now)
        self.plotSpike.set_ydata(self.data_now[channel::self.NChan])
        
        self.axSpike.set_xlim( (t_now.min(), t_now.max()) )

        # Next blue plot
        
        f.seek(self.off_nB)
        self.data_nB = np.frombuffer(f.read(4*NSamples_nB*self.NChan), dtype=np.float32)
        
        self.zLine_nB = self.axNext1.plot( (t_nB.min(), t_nB.max()), [0., 0.], 'k-.' )
        self.cLine_nB = self.axNext1.plot( (sample2plot_nB, sample2plot_nB), (saturationLow, saturationHigh), 'b-')
        self.plotNext1.set_xdata(t_nB)
        self.plotNext1.set_ydata(self.data_nB[channel::self.NChan])
        
        self.axNext1.set_xlim( (t_nB.min(), t_nB.max()) )

        # Next red plot
        
        f.seek(self.off_nR)
        self.data_nR = np.frombuffer(f.read(4*NSamples_nR*self.NChan), dtype=np.float32)
        
        self.zLine_nR = self.axNext2.plot( (t_nR.min(), t_nR.max()), [0., 0.], 'k-.' )
        self.cLine_nB = self.axNext2.plot( (sample2plot_nR, sample2plot_nR), (saturationLow, saturationHigh), 'r-')
        self.plotNext2.set_xdata(t_nR)
        self.plotNext2.set_ydata(self.data_nR[channel::self.NChan])
        
        self.axNext2.set_xlim( (t_nR.min(), t_nR.max()) )

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
