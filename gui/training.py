import os, sys

import matplotlib.pyplot as plt

from PyQt4 import QtCore, QtGui
from training_interface import Ui_trainingWindow

class TrainingWindow(QtGui.QDialog):

    def __init__(self, app, parent=None):
        self.app = app

        QtGui.QWidget.__init__(self)
        self.setFocusPolicy( QtCore.Qt.StrongFocus )
        self.setFocus()

        self.showMaximized()

        self.ui = Ui_trainingWindow()
        self.ui.setupUi(self)
        self.ui.ROCWidget.canvas.setFocusPolicy( QtCore.Qt.StrongFocus )
        self.ui.ROCWidget.canvas.setFocus()

        self.fig = self.ui.ROCWidget.canvas.fig
        self.ax = self.ui.ROCWidget.canvas.ax
       
        # Program objects -> they must be parameters for the GarbageCollector
        # do not clean them
        # If you insert a new item, it must be inserted on cancelApp method too!
        self.filterAssist1Program = QtCore.QProcess()
        self.filterAssist2Program = QtCore.QProcess()
        self.thresholdAssist1Program = QtCore.QProcess()
        self.thresholdAssist2Program = QtCore.QProcess()
        self.verifySpikes1Program = QtCore.QProcess()
        self.verifySpikes2Program = QtCore.QProcess()
        self.detectSpikes1Program = QtCore.QProcess()
        self.detectSpikes2Program = QtCore.QProcess()
        self.featuresCompute1Program = QtCore.QProcess()
        self.featuresCompute2Program = QtCore.QProcess()
        self.featuresRescalePrepareProgram = QtCore.QProcess()
        self.featuresRescaleApplyProgram = QtCore.QProcess()
        self.featuresFilterPrepareProgram = QtCore.QProcess()
        self.featuresFilterApply1Program = QtCore.QProcess()
        self.featuresFilterApply2Program = QtCore.QProcess()
        self.sliceInfo1Program = QtCore.QProcess()
        self.sliceInfo2Program = QtCore.QProcess()
        self.sliceRandom1Program = QtCore.QProcess()
        self.sliceRandom2Program = QtCore.QProcess()
        
        self.dicProgram = {'paramchooser lowpass': (self.filterAssist1Program, self.filterAssist2Program), \
                           'paramchooser threshold': (self.thresholdAssist1Program, self.thresholdAssist2Program), \
                           'winview': (self.verifySpikes1Program, self.verifySpikes2Program), \
                           'spikes Fish 1': (self.detectSpikes1Program), \
                           'spikes Fish 2': (self.detectSpikes2Program), \
                           'features compute': (self.featuresCompute1Program, self.featuresCompute2Program), \
                           'features rescale prepare': (self.featuresRescalePrepareProgram), \
                           'features rescale apply': (self.featuresRescaleApplyProgram), \
                           'features filter prepare': (self.featuresFilterPrepareProgram), \
                           'features filter apply': (self.featuresFilterApply1Program, self.featuresFilterApply2Program), \
                           'slice info': (self.sliceInfo1Program, self.sliceInfo2Program), \
                           'slice random': (self.sliceRandom1Program, self.sliceRandom2Program), \
                           }
        
        self.cancelled = False
        self.finish = False

        self.ParametersLayout = [self.ui.step1ParametersLayout, \
                self.ui.step2ParametersLayout, \
                self.ui.step3ParametersLayout, \
                self.ui.tabWidget, \
                self.ui.step5ParametersLayout, \
                ]

        self.titleLabels = [self.ui.step1TitleLabel, \
                self.ui.step2TitleLabel, \
                self.ui.step3TitleLabel, \
                self.ui.step4TitleLabel, \
                self.ui.step5TitleLabel, \
                ]

        self.defineFieldsType()

        # TODO: Pensar melhor de acordo com os lockers
        self.isLayoutShown = [False, \
        False, \
        False, \
        False, \
        False, \
        ]
        for layout in self.ParametersLayout:
            if isinstance(layout, QtGui.QLayout):
                for i in xrange(layout.count()):
                    try:
                        layout.itemAt(i).widget().hide()
                    except:
                        pass
            elif isinstance(layout, QtGui.QWidget):
                layout.hide()
        
        for label in self.titleLabels:
            QtCore.QObject.connect(label, QtCore.SIGNAL('clicked()'), self.expandLayout)
        
        # Connect load features file to load slice info
        QtCore.QObject.connect(self.ui.loadFeatures1LineEdit, QtCore.SIGNAL('textChanged(QString)'), self.sliceInfo)
        QtCore.QObject.connect(self.ui.loadFeatures2LineEdit, QtCore.SIGNAL('textChanged(QString)'), self.sliceInfo)
        
        self.connectFileFields(self.fileFieldHandler)
        self.connectUnlockFields()
        self.connectButtons()
        
        self.NWindows1 = 0.
        self.NWindows2 = 0.
        self.connectSliceFields()
        
        self.initialClickState()
    
    def connectButtons(self):
        QtCore.QObject.connect(self.ui.filterAssist1But, QtCore.SIGNAL('clicked()'), self.filterAssist1)
        QtCore.QObject.connect(self.ui.filterAssist2But, QtCore.SIGNAL('clicked()'), self.filterAssist2)
        
        QtCore.QObject.connect(self.ui.thresholdAssist1But, QtCore.SIGNAL('clicked()'), self.thresholdAssist1)
        QtCore.QObject.connect(self.ui.thresholdAssist2But, QtCore.SIGNAL('clicked()'), self.thresholdAssist2)
        
        QtCore.QObject.connect(self.ui.verifySpikes1But, QtCore.SIGNAL('clicked()'), self.verifySpikes1)
        QtCore.QObject.connect(self.ui.verifySpikes2But, QtCore.SIGNAL('clicked()'), self.verifySpikes2)
        
        QtCore.QObject.connect(self.ui.detectSpikes1But, QtCore.SIGNAL('clicked()'), self.detectSpikes1)
        QtCore.QObject.connect(self.ui.detectSpikes2But, QtCore.SIGNAL('clicked()'), self.detectSpikes2)
        
        QtCore.QObject.connect(self.ui.extractFeaturesBut, QtCore.SIGNAL('clicked()'), self.extractFeatures)
        
        QtCore.QObject.connect(self.ui.sliceFish1But, QtCore.SIGNAL('clicked()'), self.sliceRandom1)
        QtCore.QObject.connect(self.ui.sliceFish2But, QtCore.SIGNAL('clicked()'), self.sliceRandom2)
    
    def isReturnCodeOk(self, ret):
        if ret != 0:
            print '\n---\tERROR (%s): %d\t---\n'%(self.programname, ret)
            print self.dicProgram[self.programname].readAllStandardOutput()
            print self.printProgramStandardError()
            self.raiseParameterError('%s ERROR!\n'%self.programname)
            return False
        else:
            return True
    
    def printAllStandardOutput(self):
        print '%s\n'%self.programname
        print self.dicProgram[self.programname].readAllStandardOutput()
    
    def printAllStandardError(self):
        print '%s\n'%self.programname
        print self.dicProgram[self.programname].readAllStandardError()
    
    def filterAssist1(self):
        TSName = self.ui.loadTS1LineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'paramchooser lowpass'
        self.filterAssist1Program = QtCore.QProcess()
        self.filterAssist1Program.start('./../paramchooser/paramchooser', ['lowpass', TSName])
        
        def filterAssist1Finish(ret):
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                out = self.filterAssist1Program.readAllStandardOutput()
                out = out + '\n' + self.filterAssist1Program.readAllStandardError()
                
                out = str(out)
                
                numtaps = out.split('numtaps = ')[1].split('\n')[0]
                cutoff = out.split('cutoff = ')[1].split('\n')[0]
                
                self.ui.taps1LineEdit.setText(numtaps)
                self.ui.cutoff1LineEdit.setText(cutoff)
            else:
                self.cancelled = False
                return None
        
        QtCore.QObject.connect(self.filterAssist1Program, QtCore.SIGNAL('finished(int)'), filterAssist1Finish)
        
    def filterAssist2(self):
        TSName = self.ui.loadTS2LineEdit.text()
       
        # Same name of self.dicProgram
        self.programname = 'paramchooser lowpass'
        self.filterAssist2Program = QtCore.QProcess()
        self.filterAssist2Program.start('./../paramchooser/paramchooser', ['lowpass', TSName])
        
        def filterAssist2Finish(ret):
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                out = self.filterAssist2Program.readAllStandardOutput()
                out = out + '\n' + self.filterAssist2Program.readAllStandardError()
                
                out = str(out)
                
                numtaps = out.split('numtaps = ')[1].split('\n')[0]
                cutoff = out.split('cutoff = ')[1].split('\n')[0]
                
                self.ui.taps2LineEdit.setText(numtaps)
                self.ui.cutoff2LineEdit.setText(cutoff)
            else:
                self.cancelled = False
                return None
        
        QtCore.QObject.connect(self.filterAssist2Program, QtCore.SIGNAL('finished(int)'), filterAssist2Finish)
    
    def thresholdAssist1(self):
        TSName = self.ui.loadTS1LineEdit.text()
        taps = self.ui.taps1LineEdit.text()
        cutoff = self.ui.cutoff1LineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'paramchooser threshold'
        self.thresholdAssist1Program = QtCore.QProcess()
        self.thresholdAssist1Program.start('./../paramchooser/paramchooser', ['threshold', TSName, taps, cutoff])
        
        def thresholdAssist1Finish(ret):
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                out = self.thresholdAssist1Program.readAllStandardOutput()
                out = out + '\n' + self.thresholdAssist1Program.readAllStandardError()
                
                out = str(out)
                
                threshold = out.split('threshold = ')[1].split('\n')[0]
                self.ui.thresholdLevel1LineEdit.setText(threshold)
            else:
                self.cancelled = False
                return None
        
        QtCore.QObject.connect(self.thresholdAssist1Program, QtCore.SIGNAL('finished(int)'), thresholdAssist1Finish)
        
    
    def thresholdAssist2(self):
        TSName = self.ui.loadTS2LineEdit.text()
        taps = self.ui.taps2LineEdit.text()
        cutoff = self.ui.cutoff2LineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'paramchooser threshold'
        self.thresholdAssist2Program = QtCore.QProcess()
        self.thresholdAssist2Program.start('./../paramchooser/paramchooser', ['threshold', TSName, taps, cutoff])
        
        def thresholdAssist2Finish(ret):
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                out = self.thresholdAssist2Program.readAllStandardOutput()
                out = out + '\n' + self.thresholdAssist2Program.readAllStandardError()
                
                out = str(out)
                
                threshold = out.split('threshold = ')[1].split('\n')[0]
                self.ui.thresholdLevel2LineEdit.setText(threshold)
            else:
                self.cancelled = False
                return None
        
        QtCore.QObject.connect(self.thresholdAssist2Program, QtCore.SIGNAL('finished(int)'), thresholdAssist2Finish)
    
    def verifySpikes1(self):
        spikesName = self.ui.loadSpikes1LineEdit.text()
        TSName = self.ui.loadTS1LineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'winview'
        self.verifySpikes1Program = QtCore.QProcess()
        if TSName != '':
            self.verifySpikes1Program.start('./../winview/winview', [spikesName, TSName])
        else:
            self.verifySpikes1Program.start('./../winview/winview', [spikesName])
        
        def verifySpikes1Finish(ret):
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                pass
            else:
                self.cancelled = False
                return None
            
        QtCore.QObject.connect(self.verifySpikes1Program, QtCore.SIGNAL('finished(int)'), verifySpikes1Finish)
        
    def verifySpikes2(self):
        spikesName = self.ui.loadSpikes2LineEdit.text()
        TSName = self.ui.loadTS2LineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'winview'
        self.verifySpikes2Program = QtCore.QProcess()
        if TSName != '':
            self.verifySpikes2Program.start('./../winview/winview', [spikesName, TSName])
        else:
            self.verifySpikes2Program.start('./../winview/winview', [spikesName])
        
        def verifySpikes2Finish(ret):
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                pass
            else:
                self.cancelled = False
                return None
            
        QtCore.QObject.connect(self.verifySpikes2Program, QtCore.SIGNAL('finished(int)'), verifySpikes2Finish)
    
    def detectSpikes1(self):
        TSName = self.ui.loadTS1LineEdit.text()
        lowSat = self.ui.lowSaturation1LineEdit.text()
        highSat = self.ui.highSaturation1LineEdit.text()
        taps = self.ui.taps1LineEdit.text()
        cutoff = self.ui.cutoff1LineEdit.text()
        threshold = self.ui.thresholdLevel1LineEdit.text()
        saveSpikes = self.ui.saveSpikes1LineEdit.text()
        saveWindowLengths = self.ui.saveWindowLengths1LineEdit.text()
        
        dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        # Same name of self.dicProgram
        self.programname = 'spikes Fish 1'
        self.detectSpikes1Program = QtCore.QProcess()
        self.detectSpikes1Program.start('./../spikes/spikes', \
                           ['--fixedwin', \
                            '--saturation=%s,%s'%(lowSat,highSat), \
                            '--numtaps=%s'%taps, \
                            '--cutoff=%s'%cutoff, \
                            '--detection=%s'%threshold, \
                            '--winlen=%s'%saveWindowLengths, \
                            TSName, \
                            saveSpikes])
        
        def detectSpikes1Finish(ret):
            self.app.restoreOverrideCursor()
            dialog.hide()
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                self.ui.loadSpikes1LineEdit.setText(saveSpikes)
            else:
                self.cancelled = False
                return None
            
        QtCore.QObject.connect(self.detectSpikes1Program, QtCore.SIGNAL('finished(int)'), detectSpikes1Finish)
        QtCore.QObject.connect(self.detectSpikes1Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.detectSpikes1Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
        
    def detectSpikes2(self):
        TSName = self.ui.loadTS2LineEdit.text()
        lowSat = self.ui.lowSaturation2LineEdit.text()
        highSat = self.ui.highSaturation2LineEdit.text()
        taps = self.ui.taps2LineEdit.text()
        cutoff = self.ui.cutoff2LineEdit.text()
        threshold = self.ui.thresholdLevel2LineEdit.text()
        saveSpikes = self.ui.saveSpikes2LineEdit.text()
        saveWindowLengths = self.ui.saveWindowLengths2LineEdit.text()
        
        dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        # Same name of self.dicProgram
        self.programname = 'spikes Fish 2'
        self.detectSpikes2Program = QtCore.QProcess()
        self.detectSpikes2Program.start('./../spikes/spikes', \
                           ['--fixedwin', \
                            '--saturation=%s,%s'%(lowSat,highSat), \
                            '--numtaps=%s'%taps, \
                            '--cutoff=%s'%cutoff, \
                            '--detection=%s'%threshold, \
                            '--winlen=%s'%saveWindowLengths, \
                            TSName, \
                            saveSpikes])
        
        def detectSpikes2Finish(ret):
            self.app.restoreOverrideCursor()
            dialog.hide()
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                self.ui.loadSpikes2LineEdit.setText(saveSpikes)
            else:
                self.cancelled = False
                return None
            
        QtCore.QObject.connect(self.detectSpikes2Program, QtCore.SIGNAL('finished(int)'), detectSpikes2Finish)
        QtCore.QObject.connect(self.detectSpikes2Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.detectSpikes2Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
    
    def extractFeatures(self):
        self.spikesName1 = self.ui.loadSpikes1LineEdit.text()
        self.spikesName2 = self.ui.loadSpikes2LineEdit.text()
        self.unfilteredFeaturesName1 = self.ui.saveFeatures1LineEdit.text() + '_unfiltered'
        self.unfilteredFeaturesName2 = self.ui.saveFeatures2LineEdit.text() + '_unfiltered'
        self.featuresName1 = self.ui.saveFeatures1LineEdit.text()
        self.featuresName2 = self.ui.saveFeatures2LineEdit.text()
        self.filterName = self.ui.saveFilterLineEdit.text()
        self.rescaleName = self.ui.saveRescaleLineEdit.text()
        self.number = self.ui.numberFeaturesLineEdit.text()
        
        self.dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        # Will call the other functions sequentally using listeners
        self.featuresCompute() 
        
    def featuresCompute(self):
        print 'features compute'
        
        # Same name of self.dicProgram
        self.programname = 'features compute'
        
        self.finish = False
        
        self.featuresCompute1Program = QtCore.QProcess()
        self.featuresCompute1Program.start('./../features/features', \
                           ['compute', \
                            self.spikesName1, \
                            self.unfilteredFeaturesName1])
        
        self.featuresCompute2Program = QtCore.QProcess()
        self.featuresCompute2Program.start('./../features/features', \
                           ['compute', \
                            self.spikesName2, \
                            self.unfilteredFeaturesName2])
        
        def featuresComputeFinish(ret):
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                if self.finish == False:
                    self.finish = True
                else:
                    self.finish = False
                    self.featuresRescalePrepare()
            else:
                self.cancelled = False
                self.finish = False
                self.app.restoreOverrideCursor()
                self.dialog.hide()
        
        QtCore.QObject.connect(self.featuresCompute1Program, QtCore.SIGNAL('finished(int)'), featuresComputeFinish)
        QtCore.QObject.connect(self.featuresCompute2Program, QtCore.SIGNAL('finished(int)'), featuresComputeFinish)
        QtCore.QObject.connect(self.featuresCompute1Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresCompute2Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresCompute1Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        QtCore.QObject.connect(self.featuresCompute2Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
    def featuresRescalePrepare(self):        
        print 'features rescale prepare'
        
        # Same name of self.dicProgram
        self.programname = 'features rescale prepare'
        
        self.featuresRescalePrepareProgram = QtCore.QProcess()
        self.featuresRescalePrepareProgram.start('./../features/features', \
                           ['rescale', \
                            'prepare', \
                            self.rescaleName, \
                            self.unfilteredFeaturesName1, \
                            self.unfilteredFeaturesName2])
        
        def featuresRescalePrepareFinish(ret):
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                self.featuresRescaleApply()
            else:
                self.cancelled = False
                self.app.restoreOverrideCursor()
                self.dialog.hide()
                
        QtCore.QObject.connect(self.featuresRescalePrepareProgram, QtCore.SIGNAL('finished(int)'), featuresRescalePrepareFinish)
        QtCore.QObject.connect(self.featuresRescalePrepareProgram, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresRescalePrepareProgram, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
    def featuresRescaleApply(self):
        print 'features rescale apply'
        
        # Same name of self.dicProgram
        self.programname = 'features rescale apply'
        
        self.featuresRescaleApplyProgram = QtCore.QProcess()
        self.featuresRescaleApplyProgram.start('./../features/features', \
                           ['rescale', \
                            'apply', \
                            self.rescaleName, \
                            self.unfilteredFeaturesName1, \
                            self.unfilteredFeaturesName2])
        
        def featuresRescaleApplyFinish(ret):
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                self.featuresFilterPrepare()
            else:
                self.cancelled = False
                self.app.restoreOverrideCursor()
                self.dialog.hide()
        
        QtCore.QObject.connect(self.featuresRescaleApplyProgram, QtCore.SIGNAL('finished(int)'), featuresRescaleApplyFinish)
        QtCore.QObject.connect(self.featuresRescaleApplyProgram, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresRescaleApplyProgram, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
    def featuresFilterPrepare(self):
        print 'features filter prepare'
        
        # Same name of self.dicProgram
        self.programname = 'features filter prepare'
        
        self.featuresFilterPrepareProgram = QtCore.QProcess()
        self.featuresFilterPrepareProgram.start('./../features/features', \
                           ['filter', \
                            'prepare', \
                            '--best=%s'%self.number, \
                            self.filterName, \
                            self.unfilteredFeaturesName1, \
                            self.unfilteredFeaturesName2])
        
        def featuresFilterPrepareFinish(ret):
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                self.featuresFilterApply()
            else:
                self.cancelled = False
                self.app.restoreOverrideCursor()
                self.dialog.hide()
                
        QtCore.QObject.connect(self.featuresFilterPrepareProgram, QtCore.SIGNAL('finished(int)'), featuresFilterPrepareFinish)
        QtCore.QObject.connect(self.featuresFilterPrepareProgram, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresFilterPrepareProgram, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
        
    def featuresFilterApply(self):
        print 'features filter apply'
        
        # Same name of self.dicProgram
        self.programname = 'features filter apply'
        
        self.finish = False
        
        self.featuresFilterApply1Program = QtCore.QProcess()
        self.featuresFilterApply1Program.start('./../features/features', \
                           ['filter', \
                            'apply', \
                            self.filterName, \
                            self.unfilteredFeaturesName1, \
                            self.featuresName1])
        
        self.featuresFilterApply2Program = QtCore.QProcess()
        self.featuresFilterApply2Program.start('./../features/features', \
                           ['filter', \
                            'apply', \
                            self.filterName, \
                            self.unfilteredFeaturesName2, \
                            self.featuresName2])
        
        def featuresFilterApplyFinish(ret):
            if (self.isReturnCodeOk(ret) is True) and (self.cancelled is False):
                if self.finish == False:
                    self.finish = True
                else:
                    self.finish = False
                    self.featuresFinish()
            else:
                self.cancelled = False
                self.finish = False
                self.app.restoreOverrideCursor()
                self.dialog.hide()
        
        QtCore.QObject.connect(self.featuresFilterApply1Program, QtCore.SIGNAL('finished(int)'), featuresFilterApplyFinish)
        QtCore.QObject.connect(self.featuresFilterApply2Program, QtCore.SIGNAL('finished(int)'), featuresFilterApplyFinish)
        QtCore.QObject.connect(self.featuresFilterApply1Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresFilterApply2Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresFilterApply1Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        QtCore.QObject.connect(self.featuresFilterApply2Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
    def featuresFinish(self):
        print 'end features'
        self.ui.loadFeatures1LineEdit.setText(self.featuresName1)
        self.ui.loadFeatures2LineEdit.setText(self.featuresName2)
        os.remove(self.unfilteredFeaturesName1)
        os.remove(self.unfilteredFeaturesName2)
        self.app.restoreOverrideCursor()
        self.dialog.hide()
    
    def sliceInfo(self, filename):
        print 'slice info'
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        field = self.sender()
        featuresName = field.text()
        
        def fillInfoLabel1(ret):
            self.app.restoreOverrideCursor()
            if self.isReturnCodeOk(ret) is True:
                stdout = self.sliceInfo1Program.readAllStandardOutput()
                stderr = self.sliceInfo1Program.readAllStandardError()
                if stdout != '':
                    text, self.NWindows1 = self.formatInfoText(str(stdout))
                else:
                    text, self.NWindows1 = self.formatInfoText(str(stderr))
                self.ui.sliceInfoFish1Label.setText(text)
            else:
                return None
        
        def fillInfoLabel2(ret):
            self.app.restoreOverrideCursor()
            if self.isReturnCodeOk(ret) is True:
                stdout = self.sliceInfo2Program.readAllStandardOutput()
                stderr = self.sliceInfo2Program.readAllStandardError()
                if stdout != '':
                    text, self.NWindows2 = self.formatInfoText(str(stdout))
                else:
                    text, self.NWindows2 = self.formatInfoText(str(stderr))
                self.ui.sliceInfoFish2Label.setText(text)
            else:
                return None
        
        # If they are executed at the same time, the program variable cannot be overriden
        # by the Garbage Collector
        if os.path.isfile(featuresName):
            if field == self.ui.loadFeatures1LineEdit:
                self.sliceInfo1Program = QtCore.QProcess()
                self.sliceInfo1Program.start('./../slice/slice', \
                                             ['info', \
                                              featuresName])
                QtCore.QObject.connect(self.sliceInfo1Program, QtCore.SIGNAL('finished(int)'), fillInfoLabel1)
            else:
                self.sliceInfo2Program = QtCore.QProcess()
                self.sliceInfo2Program.start('./../slice/slice', \
                                             ['info', \
                                              featuresName])
                QtCore.QObject.connect(self.sliceInfo2Program, QtCore.SIGNAL('finished(int)'), fillInfoLabel2)
   
    def sliceRandom1(self):
        featuresName = self.ui.loadFeatures1LineEdit.text()
        probTrain = float(self.ui.trainingProbabilityFish1LineEdit.text())
        saveTrain = self.ui.trainingSaveFish1LineEdit.text()
        probCross = float(self.ui.crossProbabilityFish1LineEdit.text())
        saveCross = self.ui.crossSaveFish1LineEdit.text()
        probTest = float(self.ui.testingProbabilityFish1LineEdit.text())
        saveTest = self.ui.testingSaveFish1LineEdit.text()
        
        if (0 <= probTrain <= 1) and \
           (0 <= probCross <= 1) and \
           (0 <= probTest <= 1) and \
           (0 <= probTrain + probCross + probTest <= 1):
            print 'slice random'
            self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            
            self.programName = 'slice random'
            
            self.sliceRandom1Program = QtCore.QProcess()
            self.sliceRandom1Program.start('./../slice/slice', \
                                           ['random', \
                                            featuresName, \
                                            str(probTrain), saveTrain, \
                                            str(probCross), saveCross, \
                                            str(probTest), saveTest])
            
            def sliceRandomFinish(ret):
                self.app.restoreOverrideCursor()
                if self.isReturnCodeOk(ret) is True:
                    self.ui.trainingLoadFish1LineEdit.setText(self.ui.trainingSaveFish1LineEdit.text())
                    self.ui.crossLoadFish1LineEdit.setText(self.ui.crossSaveFish1LineEdit.text())
                    self.ui.testingLoadFish1LineEdit.setText(self.ui.testingSaveFish1LineEdit.text())
            
            QtCore.QObject.connect(self.sliceRandom1Program, QtCore.SIGNAL('finished(int)'), sliceRandomFinish)
            QtCore.QObject.connect(self.sliceRandom1Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
            QtCore.QObject.connect(self.sliceRandom1Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        else:
            QtGui.QMessageBox.critical(self, "ERROR", 'Please check your parameters!\nAll the probabilities and their sum must be on the interval [0,1]', QtGui.QMessageBox.Ok)
    
    def sliceRandom2(self):
        featuresName = self.ui.loadFeatures2LineEdit.text()
        probTrain = float(self.ui.trainingProbabilityFish2LineEdit.text())
        saveTrain = self.ui.trainingSaveFish2LineEdit.text()
        probCross = float(self.ui.crossProbabilityFish2LineEdit.text())
        saveCross = self.ui.crossSaveFish2LineEdit.text()
        probTest = float(self.ui.testingProbabilityFish2LineEdit.text())
        saveTest = self.ui.testingSaveFish2LineEdit.text()
        
        if (0 <= probTrain <= 1) and \
           (0 <= probCross <= 1) and \
           (0 <= probTest <= 1) and \
           (0 <= probTrain + probCross + probTest <= 1):
            print 'slice random'
            self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            
            self.programName = 'slice random'
            
            self.sliceRandom2Program = QtCore.QProcess()
            self.sliceRandom2Program.start('./../slice/slice', \
                                           ['random', \
                                            featuresName, \
                                            str(probTrain), saveTrain, \
                                            str(probCross), saveCross, \
                                            str(probTest), saveTest])
            
            def sliceRandomFinish(ret):
                self.app.restoreOverrideCursor()
                if self.isReturnCodeOk(ret) is True:
                    self.ui.trainingLoadFish2LineEdit.setText(self.ui.trainingSaveFish2LineEdit.text())
                    self.ui.crossLoadFish2LineEdit.setText(self.ui.crossSaveFish2LineEdit.text())
                    self.ui.testingLoadFish2LineEdit.setText(self.ui.testingSaveFish2LineEdit.text())
            
            QtCore.QObject.connect(self.sliceRandom2Program, QtCore.SIGNAL('finished(int)'), sliceRandomFinish)
            QtCore.QObject.connect(self.sliceRandom2Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
            QtCore.QObject.connect(self.sliceRandom2Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        else:
            QtGui.QMessageBox.critical(self, "ERROR", 'Please check your parameters!\nAll the probabilities and their sum must be on the interval [0,1]', QtGui.QMessageBox.Ok)
    
    def formatInfoText(self,text):
        NWindows = int(text.split('\n')[-3].split(' ')[-1])
        output = ''
        for line in text.split('\n')[-5:]:
            output = output + line + '\n'
        output = output.strip()
        return (output, NWindows)
    
    def fileFieldHandler(self):
        field = self.sender()
        # TODO: define saving path
        path = ''
        fileFilter = QtCore.QString(self.fileFieldsExtension[field]) + QtCore.QString(';;All files (*.*) (*.*)')
        if self.fieldsType[field] == 'load':
            filename = QtGui.QFileDialog.getOpenFileName(self, 'Load file', path, fileFilter)
        elif self.fieldsType[field] == 'save':
            filename = QtGui.QFileDialog.getSaveFileName( self, 'Save file', path, fileFilter )
        if filename != '':
            field.setText(filename)
        else:
            pass
    
    def raiseLongTimeInformation(self):
        dialog = QtGui.QMessageBox()
        dialog.setWindowTitle('Information')
        dialog.setText("This may take a while...\nTime for a coffee!\n")
        dialog.setModal(True)
        self.CancelBut = dialog.addButton(QtGui.QMessageBox.Cancel)
        QtCore.QObject.connect(self.CancelBut, QtCore.SIGNAL('clicked()'), self.cancelApp)
        dialog.show()
        return dialog
    
    def raiseParameterError(self, text):
        QtGui.QMessageBox.critical(self, "ERROR", text + "Please check your parameters.", QtGui.QMessageBox.Ok )
    
    def cancelApp(self):
        self.cancelled = True
        self.filterAssist1Program.terminate()
        self.filterAssist2Program.terminate()
        self.thresholdAssist1Program.terminate()
        self.thresholdAssist2Program.terminate()
        self.verifySpikes1Program.terminate()
        self.verifySpikes2Program.terminate()
        self.detectSpikes1Program.terminate()
        self.detectSpikes2Program.terminate()
        self.featuresCompute1Program.terminate()
        self.featuresCompute2Program.terminate()
        self.featuresRescalePrepareProgram.terminate()
        self.featuresRescaleApplyProgram.terminate()
        self.featuresFilterPrepareProgram.terminate()
        self.featuresFilterApply1Program.terminate()
        self.featuresFilterApply2Program.terminate()
    
    def defineFieldsType(self):
        self.fieldsType = {self.ui.loadTS1LineEdit: 'load', \
                       
                       self.ui.loadTS2LineEdit: 'load', \
                       
                       self.ui.lowSaturation1LineEdit: 'float', \
                       self.ui.highSaturation1LineEdit: 'float', \
                       self.ui.taps1LineEdit: 'int', \
                       self.ui.cutoff1LineEdit: 'float', \
                       self.ui.thresholdLevel1LineEdit: 'float', \
                       
                       self.ui.lowSaturation2LineEdit: 'float', \
                       self.ui.highSaturation2LineEdit: 'float', \
                       self.ui.taps2LineEdit: 'int', \
                       self.ui.cutoff2LineEdit: 'float', \
                       self.ui.thresholdLevel2LineEdit: 'float', \
                       
                       self.ui.saveSpikes1LineEdit: 'save', \
                       self.ui.saveWindowLengths1LineEdit: 'save', \
                       
                       self.ui.saveSpikes2LineEdit: 'save', \
                       self.ui.saveWindowLengths2LineEdit: 'save', \
                       
                       self.ui.loadSpikes1LineEdit: 'load', \
                       
                       self.ui.loadSpikes2LineEdit: 'load', \
                       
                       self.ui.saveFeatures1LineEdit: 'save', \
                       self.ui.saveFeatures2LineEdit: 'save', \
                       self.ui.saveFilterLineEdit: 'save', \
                       self.ui.saveRescaleLineEdit: 'save', \
                       self.ui.numberFeaturesLineEdit: 'int', \
                       
                       self.ui.loadFeatures1LineEdit: 'load', \
                       
                       self.ui.loadFeatures2LineEdit: 'load', \
                       
                       self.ui.trainingNumberSamplesFish1LineEdit: 'int', \
                       self.ui.trainingProbabilityFish1LineEdit: 'float', \
                       self.ui.trainingSaveFish1LineEdit: 'save', \
                       self.ui.crossNumberSamplesFish1LineEdit: 'int', \
                       self.ui.crossProbabilityFish1LineEdit: 'float', \
                       self.ui.crossSaveFish1LineEdit: 'save', \
                       self.ui.testingNumberSamplesFish1LineEdit: 'int', \
                       self.ui.testingProbabilityFish1LineEdit: 'float', \
                       self.ui.testingSaveFish1LineEdit: 'save', \
                       
                       self.ui.trainingNumberSamplesFish2LineEdit: 'int', \
                       self.ui.trainingProbabilityFish2LineEdit: 'float', \
                       self.ui.trainingSaveFish2LineEdit: 'save', \
                       self.ui.crossNumberSamplesFish2LineEdit: 'int', \
                       self.ui.crossProbabilityFish2LineEdit: 'float', \
                       self.ui.crossSaveFish2LineEdit: 'save', \
                       self.ui.testingNumberSamplesFish2LineEdit: 'int', \
                       self.ui.testingProbabilityFish2LineEdit: 'float', \
                       self.ui.testingSaveFish2LineEdit: 'save', \
                       
                       self.ui.trainingLoadFish1LineEdit: 'load', \
                       self.ui.trainingLoadFish2LineEdit: 'load', \
                       self.ui.crossLoadFish1LineEdit: 'load', \
                       self.ui.crossLoadFish2LineEdit: 'load', \
                       
                       self.ui.cStartLineEdit: 'float', \
                       self.ui.cStepLineEdit: 'float', \
                       self.ui.cStopLineEdit: 'float', \
                       self.ui.gStartLineEdit: 'float', \
                       self.ui.gStepLineEdit: 'float', \
                       self.ui.gStopLineEdit: 'float', \
                       
                       self.ui.cValueLineEdit: 'float', \
                       self.ui.gValueLineEdit: 'float', \
                       self.ui.saveSVMLineEdit: 'save', \
                       
                       self.ui.loadSVMLineEdit: 'load', \
                       self.ui.testingLoadFish1LineEdit: 'load', \
                       self.ui.testingLoadFish2LineEdit: 'load', \
                       }
        
        for field in self.fieldsType.keys():
            if self.fieldsType[field] == 'int':
                field.setValidator( QtGui.QIntValidator() )
            elif self.fieldsType[field] == 'float':
                field.setValidator( QtGui.QDoubleValidator() )
        
        self.fileFieldsExtension = {
            self.ui.loadTS1LineEdit: 'Timeseries on format I32 file (*.*) (*.*)', \
            self.ui.loadTS2LineEdit: 'Timeseries on format I32 file (*.*) (*.*)', \
            self.ui.saveSpikes1LineEdit: 'Spikes File (*.spikes) (*.spikes)', \
            self.ui.saveSpikes2LineEdit: 'Spikes File (*.spikes) (*.spikes)', \
            self.ui.loadSpikes1LineEdit: 'Spikes File (*.spikes) (*.spikes)', \
            self.ui.loadSpikes2LineEdit: 'Spikes File (*.spikes) (*.spikes)', \
            self.ui.saveWindowLengths1LineEdit: 'Window Length File (*.winlen) (*.winlen)', \
            self.ui.saveWindowLengths2LineEdit: 'Window Length File (*.winlen) (*.winlen)', \
            self.ui.saveFeatures1LineEdit: 'Features File (*.features) (*.features)', \
            self.ui.saveFeatures2LineEdit: 'Features File (*.features) (*.features)', \
            self.ui.loadFeatures1LineEdit: 'Features File (*.features) (*.features)', \
            self.ui.loadFeatures2LineEdit: 'Features File (*.features) (*.features)', \
            self.ui.saveFilterLineEdit: 'Filter File (*.filter) (*.filter)', \
            self.ui.saveRescaleLineEdit: 'Rescale File (*.scale) (*.scale)', \
            self.ui.trainingSaveFish1LineEdit: 'Training set File (*.training) (*.training)', \
            self.ui.trainingSaveFish2LineEdit: 'Training set File (*.training) (*.training)', \
            self.ui.trainingLoadFish1LineEdit: 'Training set File (*.training) (*.training)', \
            self.ui.trainingLoadFish2LineEdit: 'Training set File (*.training) (*.training)', \
            self.ui.crossSaveFish1LineEdit: 'Cross Validation set File (*.cross) (*.cross)', \
            self.ui.crossSaveFish2LineEdit: 'Cross Validation set File (*.cross) (*.cross)', \
            self.ui.crossLoadFish1LineEdit: 'Cross Validation set File (*.cross) (*.cross)', \
            self.ui.crossLoadFish2LineEdit: 'Cross Validation set File (*.cross) (*.cross)', \
            self.ui.testingSaveFish1LineEdit: 'Testing set File (*.testing) (*.testing)', \
            self.ui.testingSaveFish2LineEdit: 'Testing set File (*.testing) (*.testing)', \
            self.ui.testingLoadFish1LineEdit: 'Testing set File (*.testing) (*.testing)', \
            self.ui.testingLoadFish2LineEdit: 'Testing set File (*.testing) (*.testing)', \
            self.ui.saveSVMLineEdit: 'SVM Model File (*.svmmodel) (*.svmmodel)', \
            self.ui.loadSVMLineEdit: 'SVM Model File (*.svmmodel) (*.svmmodel)', \
            }
    
    def connectSliceFields(self):
        fish1Fields = (self.ui.trainingNumberSamplesFish1LineEdit, \
                       self.ui.crossNumberSamplesFish1LineEdit, \
                       self.ui.testingNumberSamplesFish1LineEdit, \
                       self.ui.trainingProbabilityFish1LineEdit, \
                       self.ui.crossProbabilityFish1LineEdit, \
                       self.ui.testingProbabilityFish1LineEdit, \
                       )
        fish2Fields = (self.ui.trainingNumberSamplesFish2LineEdit, \
                       self.ui.crossNumberSamplesFish2LineEdit, \
                       self.ui.testingNumberSamplesFish2LineEdit, \
                       self.ui.trainingProbabilityFish2LineEdit, \
                       self.ui.crossProbabilityFish2LineEdit, \
                       self.ui.testingProbabilityFish2LineEdit, \
                       )
        
        self.testingDependency = (self.ui.trainingNumberSamplesFish1LineEdit, 
                                   self.ui.crossNumberSamplesFish1LineEdit, \
                                   self.ui.trainingProbabilityFish1LineEdit, \
                                   self.ui.crossProbabilityFish1LineEdit, \
                                   self.ui.trainingNumberSamplesFish2LineEdit, 
                                   self.ui.crossNumberSamplesFish2LineEdit, \
                                   self.ui.trainingProbabilityFish2LineEdit, \
                                   self.ui.crossProbabilityFish2LineEdit)
        
        self.sliceFieldsNSamples_Prob = { \
        self.ui.trainingNumberSamplesFish1LineEdit: self.ui.trainingProbabilityFish1LineEdit, \
        self.ui.trainingNumberSamplesFish2LineEdit: self.ui.trainingProbabilityFish2LineEdit, \
        self.ui.crossNumberSamplesFish1LineEdit: self.ui.crossProbabilityFish1LineEdit, \
        self.ui.crossNumberSamplesFish2LineEdit: self.ui.crossProbabilityFish2LineEdit, \
        self.ui.testingNumberSamplesFish1LineEdit: self.ui.testingProbabilityFish1LineEdit, \
        self.ui.testingNumberSamplesFish2LineEdit: self.ui.testingProbabilityFish2LineEdit, \
        }
        
        self.sliceFieldsProb_NSamples = {v:k for k,v in self.sliceFieldsNSamples_Prob.items()}
        
        def numberSamplesConnection(text):
            NSamplesField = self.sender()
            
            ProbField = self.sliceFieldsNSamples_Prob[NSamplesField]
            ProbField.blockSignals(True)
            
            if NSamplesField in fish1Fields:
                fish = 1
            else:
                fish = 2
            
            if fish == 1:
                prob = float(text) / float(self.NWindows1)
            else:
                prob = float(text) / float(self.NWindows2)
            
            if prob < 0 or prob > 1:
                NSamplesField.setStyleSheet('QLineEdit { background-color: #ff0000; }')
                ProbField.setStyleSheet('QLineEdit { background-color: #ff0000; }')
            else:
                NSamplesField.setStyleSheet('QLineEdit { background-color: #ffffff; }')
                ProbField.setStyleSheet('QLineEdit { background-color: #ffffff; }')
            
            ProbField.setText(str(prob))
            ProbField.blockSignals(False)
        
        def probabilityConnection(prob):
            ProbField = self.sender()
            # If the string is incomplete, do not print error message
            try:
                prob = float(prob)
            except:
                return None
            
            NSamplesField = self.sliceFieldsProb_NSamples[ProbField]
            NSamplesField.blockSignals(True)
            
            if ProbField in fish1Fields:
                fish = 1
            else:
                fish = 2
            
            if prob < 0 or prob > 1:
                NSamplesField.setStyleSheet('QLineEdit { background-color: #ff0000; }')
                ProbField.setStyleSheet('QLineEdit { background-color: #ff0000; }')
            else:
                NSamplesField.setStyleSheet('QLineEdit { background-color: #ffffff; }')
                ProbField.setStyleSheet('QLineEdit { background-color: #ffffff; }')
            
            if fish == 1:
                NSamples = int(round(prob * float(self.NWindows1)))
            else:
                NSamples = int(round(prob * float(self.NWindows2)))
            
            NSamplesField.setText(str(NSamples))
            NSamplesField.blockSignals(False)
        
        for field in self.sliceFieldsNSamples_Prob.keys():
            QtCore.QObject.connect(field, QtCore.SIGNAL('textChanged(QString)'), numberSamplesConnection)
        for field in self.sliceFieldsProb_NSamples.keys():
            QtCore.QObject.connect(field, QtCore.SIGNAL('textChanged(QString)'), probabilityConnection)
        
        def updateTesting(text):
            sender = self.sender()
            if sender in fish1Fields:
                fish = 1
            else:
                fish = 2
            
            if fish == 1:
                trainingNSamples = self.ui.trainingNumberSamplesFish1LineEdit.text()
                crossNSamples = self.ui.crossNumberSamplesFish1LineEdit.text()
                totalSamples = self.NWindows1
                outField = self.ui.testingNumberSamplesFish1LineEdit
            else:
                trainingNSamples = self.ui.trainingNumberSamplesFish2LineEdit.text()
                crossNSamples = self.ui.crossNumberSamplesFish2LineEdit.text()
                totalSamples = self.NWindows2
                outField = self.ui.testingNumberSamplesFish2LineEdit
            
            if trainingNSamples == '' or crossNSamples == '' or totalSamples == '':
                outField.setText('')
                return None
            
            output = str(int(totalSamples) - (int(trainingNSamples) + int(crossNSamples)))
            outField.setText(output)
            
        for field in self.testingDependency:
            QtCore.QObject.connect(field, QtCore.SIGNAL('textChanged(QString)'), updateTesting)
        
    
    def connectUnlockFields(self):
        
        # The first element of the unlockers is the list of fields that block others
        # The second element are the fields that are release by that edition
        self.loadTSFish1Unlocker = ( \
            ( \
                (self.ui.loadTS1LineEdit, \
                 ), \
                (self.ui.lowSaturation1LineEdit, \
                 self.ui.highSaturation1LineEdit, \
                 self.ui.taps1LineEdit, \
                 self.ui.cutoff1LineEdit, \
                 self.ui.filterAssist1But,
                 ) \
            ), \
        )
        
        self.loadTSFish2Unlocker = ( \
            ( \
                (self.ui.loadTS2LineEdit, \
                 ), \
                (self.ui.lowSaturation2LineEdit, \
                 self.ui.highSaturation2LineEdit, \
                 self.ui.taps2LineEdit, \
                 self.ui.cutoff2LineEdit, \
                 self.ui.filterAssist2But, \
                 ) \
            ), \
        )
        
        self.spikeParametersFish1Unlocker = ( \
            ( \
                (self.ui.lowSaturation1LineEdit, \
                 self.ui.highSaturation1LineEdit, \
                 self.ui.taps1LineEdit, \
                 self.ui.cutoff1LineEdit, \
                 self.ui.thresholdLevel1LineEdit, \
                 ), \
                (self.ui.saveSpikes1LineEdit, \
                 self.ui.saveWindowLengths1LineEdit, \
                ) \
            ), \
            ( \
                (self.ui.taps1LineEdit, \
                 self.ui.cutoff1LineEdit, \
                 ), \
                (self.ui.thresholdAssist1But, \
                 self.ui.thresholdLevel1LineEdit, \
                 ) \
            ), \
        )
        
        self.spikeParametersFish2Unlocker = ( \
            ( \
                (self.ui.lowSaturation2LineEdit, \
                 self.ui.highSaturation2LineEdit, \
                 self.ui.taps2LineEdit, \
                 self.ui.cutoff2LineEdit, \
                 self.ui.thresholdLevel2LineEdit, \
                 ), \
                (self.ui.saveSpikes2LineEdit, \
                 self.ui.saveWindowLengths2LineEdit, \
                ) \
            ), \
            ( \
                (self.ui.taps2LineEdit, \
                 self.ui.cutoff2LineEdit, \
                 ), \
                (self.ui.thresholdAssist2But, \
                 self.ui.thresholdLevel2LineEdit, \
                 ) \
            ), \
        )
        
        self.spikeSavefilesFish1Unlocker = ( \
            ( \
                (self.ui.saveSpikes1LineEdit, \
                 self.ui.saveWindowLengths1LineEdit, \
                 ), \
                (self.ui.detectSpikes1But, \
                ) \
            ), \
        )
        
        self.spikeSavefilesFish2Unlocker = ( \
            ( \
                (self.ui.saveSpikes2LineEdit, \
                 self.ui.saveWindowLengths2LineEdit, \
                 ), \
                (self.ui.detectSpikes2But, \
                 ) \
            ), \
        )
        
        self.loadSpikesFish1Unlocker = ( \
            ( \
                (self.ui.loadSpikes1LineEdit, \
                 ), \
                (self.ui.verifySpikes1But, \
                 ) \
            ), \
            ( \
                (self.ui.loadSpikes1LineEdit, \
                 self.ui.loadSpikes2LineEdit, \
                 ), \
                (self.ui.saveFeatures1LineEdit, \
                 self.ui.saveFeatures2LineEdit, \
                 self.ui.saveFilterLineEdit, \
                 self.ui.saveRescaleLineEdit, \
                 self.ui.numberFeaturesLineEdit, \
                 ) \
            ), \
        )
        
        self.loadSpikesFish2Unlocker = ( \
            ( \
                (self.ui.loadSpikes2LineEdit, \
                 ), \
                (self.ui.verifySpikes2But, \
                 ) \
            ), \
            ( \
                (self.ui.loadSpikes1LineEdit, \
                 self.ui.loadSpikes2LineEdit, \
                 ), \
                (self.ui.saveFeatures1LineEdit, \
                 self.ui.saveFeatures2LineEdit, \
                 self.ui.saveFilterLineEdit, \
                 self.ui.saveRescaleLineEdit, \
                 self.ui.numberFeaturesLineEdit, \
                 ) \
            ), \
        )
        
        self.featuresParametersUnlocker = ( \
            ( \
                (self.ui.saveFeatures1LineEdit, \
                 self.ui.saveFeatures2LineEdit, \
                 self.ui.saveFilterLineEdit, \
                 self.ui.saveRescaleLineEdit, \
                 self.ui.numberFeaturesLineEdit, \
                 ), \
                (self.ui.extractFeaturesBut, \
                 ) \
            ), \
        )
        
        self.loadFeaturesFish1Unlocker = ( \
            ( \
                (self.ui.loadFeatures1LineEdit, \
                 ), \
                (self.ui.trainingNumberSamplesFish1LineEdit, \
                self.ui.crossNumberSamplesFish1LineEdit, \
                
                self.ui.trainingProbabilityFish1LineEdit, \
                self.ui.crossProbabilityFish1LineEdit, \
                
                self.ui.trainingSaveFish1LineEdit, \
                self.ui.crossSaveFish1LineEdit, \
                self.ui.testingSaveFish1LineEdit, \
                ) \
            ), \
        )
        
        self.loadFeaturesFish2Unlocker = ( \
            ( \
                (self.ui.loadFeatures2LineEdit, \
                 ), \
                (self.ui.trainingNumberSamplesFish2LineEdit, \
                self.ui.crossNumberSamplesFish2LineEdit, \
                
                self.ui.trainingProbabilityFish2LineEdit, \
                self.ui.crossProbabilityFish2LineEdit, \
                
                self.ui.trainingSaveFish2LineEdit, \
                self.ui.crossSaveFish2LineEdit, \
                self.ui.testingSaveFish2LineEdit, \
                ) \
            ), \
        )
        
        self.sliceParametersFish1Unlocker = ( \
            ( \
                (self.ui.trainingNumberSamplesFish1LineEdit, \
                 self.ui.trainingProbabilityFish1LineEdit, \
                 self.ui.trainingSaveFish1LineEdit, \
                 self.ui.crossNumberSamplesFish1LineEdit, \
                 self.ui.crossProbabilityFish1LineEdit, \
                 self.ui.crossSaveFish1LineEdit, \
                 self.ui.testingNumberSamplesFish1LineEdit, \
                 self.ui.testingProbabilityFish1LineEdit, \
                 self.ui.testingSaveFish1LineEdit, \
                 ), \
                (self.ui.sliceFish1But, \
                ) \
            ), \
        )
        
        self.sliceParametersFish2Unlocker = ( \
            ( \
                (self.ui.trainingNumberSamplesFish2LineEdit, \
                 self.ui.trainingProbabilityFish2LineEdit, \
                 self.ui.trainingSaveFish2LineEdit, \
                 self.ui.crossNumberSamplesFish2LineEdit, \
                 self.ui.crossProbabilityFish2LineEdit, \
                 self.ui.crossSaveFish2LineEdit, \
                 self.ui.testingNumberSamplesFish2LineEdit, \
                 self.ui.testingProbabilityFish2LineEdit, \
                 self.ui.testingSaveFish2LineEdit, \
                 ), \
                (self.ui.sliceFish2But, \
                 ) \
            ), \
        )
        
        self.loadSliceUnlocker = ( \
            ( \
                (self.ui.trainingLoadFish1LineEdit, \
                 self.ui.trainingLoadFish2LineEdit, \
                 self.ui.crossLoadFish1LineEdit, \
                 self.ui.crossLoadFish2LineEdit, \
                 
                 ), \
                (self.ui.defaultValuesBut, \
                 self.ui.cStartLineEdit, \
                 self.ui.cStepLineEdit, \
                 self.ui.cStopLineEdit, \
                 self.ui.cValueLineEdit, \
                 self.ui.gStartLineEdit, \
                 self.ui.gStepLineEdit, \
                 self.ui.gStopLineEdit, \
                 self.ui.gValueLineEdit, \
                ) \
            ), \
        )
        
        self.SVMGridUnlocker = ( \
            ( \
                (self.ui.cStartLineEdit, \
                 self.ui.cStepLineEdit, \
                 self.ui.cStopLineEdit, \
                 self.ui.gStartLineEdit, \
                 self.ui.gStepLineEdit, \
                 self.ui.gStopLineEdit, \
                 
                 ), \
                (self.ui.optimizeSVMBut, \
                 ) \
            ), \
        )
        
        self.SVMParametersUnlocker = ( \
            ( \
                (self.ui.cValueLineEdit, \
                 self.ui.gValueLineEdit, \
                 
                 ), \
                (self.ui.saveSVMLineEdit, \
                 ) \
            ), \
        )
        
        self.saveSVMUnlocker = ( \
        ( \
            (self.ui.saveSVMLineEdit, \
             
             ), \
            (self.ui.trainSVMBut, \
             ) \
        ), \
        )
        
        self.testingAndSVMUnlocker = ( \
            ( \
                (self.ui.testingLoadFish1LineEdit, \
                 self.ui.testingLoadFish2LineEdit, \
                 self.ui.loadSVMLineEdit, \
                 
                 ), \
                (self.ui.generateROCBut, \
                 ) \
            ), \
        )
        
        self.Fields = {self.ui.loadTS1LineEdit: self.loadTSFish1Unlocker, \
                       
                       self.ui.loadTS2LineEdit: self.loadTSFish2Unlocker, \
                       
                       self.ui.lowSaturation1LineEdit: self.spikeParametersFish1Unlocker, \
                       self.ui.highSaturation1LineEdit: self.spikeParametersFish1Unlocker, \
                       self.ui.taps1LineEdit: self.spikeParametersFish1Unlocker, \
                       self.ui.cutoff1LineEdit: self.spikeParametersFish1Unlocker, \
                       self.ui.thresholdLevel1LineEdit: self.spikeParametersFish1Unlocker, \
                       
                       self.ui.lowSaturation2LineEdit: self.spikeParametersFish2Unlocker, \
                       self.ui.highSaturation2LineEdit: self.spikeParametersFish2Unlocker, \
                       self.ui.taps2LineEdit: self.spikeParametersFish2Unlocker, \
                       self.ui.cutoff2LineEdit: self.spikeParametersFish2Unlocker, \
                       self.ui.thresholdLevel2LineEdit: self.spikeParametersFish2Unlocker, \
                       
                       self.ui.saveSpikes1LineEdit: self.spikeSavefilesFish1Unlocker, \
                       self.ui.saveWindowLengths1LineEdit: self.spikeSavefilesFish1Unlocker, \
                       
                       self.ui.saveSpikes2LineEdit: self.spikeSavefilesFish2Unlocker, \
                       self.ui.saveWindowLengths2LineEdit: self.spikeSavefilesFish2Unlocker, \
                       
                       self.ui.loadSpikes1LineEdit: self.loadSpikesFish1Unlocker, \
                       
                       self.ui.loadSpikes2LineEdit: self.loadSpikesFish2Unlocker, \
                       
                       self.ui.saveFeatures1LineEdit: self.featuresParametersUnlocker, \
                       self.ui.saveFeatures2LineEdit: self.featuresParametersUnlocker, \
                       self.ui.saveFilterLineEdit: self.featuresParametersUnlocker, \
                       self.ui.saveRescaleLineEdit: self.featuresParametersUnlocker, \
                       self.ui.numberFeaturesLineEdit: self.featuresParametersUnlocker, \
                       
                       self.ui.loadFeatures1LineEdit: self.loadFeaturesFish1Unlocker, \
                       
                       self.ui.loadFeatures2LineEdit: self.loadFeaturesFish2Unlocker, \
                       
                       self.ui.trainingNumberSamplesFish1LineEdit: self.sliceParametersFish1Unlocker, \
                       self.ui.trainingProbabilityFish1LineEdit: self.sliceParametersFish1Unlocker, \
                       self.ui.trainingSaveFish1LineEdit: self.sliceParametersFish1Unlocker, \
                       self.ui.crossNumberSamplesFish1LineEdit: self.sliceParametersFish1Unlocker, \
                       self.ui.crossProbabilityFish1LineEdit: self.sliceParametersFish1Unlocker, \
                       self.ui.crossSaveFish1LineEdit: self.sliceParametersFish1Unlocker, \
                       self.ui.testingNumberSamplesFish1LineEdit: self.sliceParametersFish1Unlocker, \
                       self.ui.testingProbabilityFish1LineEdit: self.sliceParametersFish1Unlocker, \
                       self.ui.testingSaveFish1LineEdit: self.sliceParametersFish1Unlocker, \
                       
                       self.ui.trainingNumberSamplesFish2LineEdit: self.sliceParametersFish2Unlocker, \
                       self.ui.trainingProbabilityFish2LineEdit: self.sliceParametersFish2Unlocker, \
                       self.ui.trainingSaveFish2LineEdit: self.sliceParametersFish2Unlocker, \
                       self.ui.crossNumberSamplesFish2LineEdit: self.sliceParametersFish2Unlocker, \
                       self.ui.crossProbabilityFish2LineEdit: self.sliceParametersFish2Unlocker, \
                       self.ui.crossSaveFish2LineEdit: self.sliceParametersFish2Unlocker, \
                       self.ui.testingNumberSamplesFish2LineEdit: self.sliceParametersFish2Unlocker, \
                       self.ui.testingProbabilityFish2LineEdit: self.sliceParametersFish2Unlocker, \
                       self.ui.testingSaveFish2LineEdit: self.sliceParametersFish2Unlocker, \
                       
                       self.ui.trainingLoadFish1LineEdit: self.loadSliceUnlocker, \
                       self.ui.trainingLoadFish2LineEdit: self.loadSliceUnlocker, \
                       self.ui.crossLoadFish1LineEdit: self.loadSliceUnlocker, \
                       self.ui.crossLoadFish2LineEdit: self.loadSliceUnlocker, \
                       
                       self.ui.cStartLineEdit: self.SVMGridUnlocker, \
                       self.ui.cStepLineEdit: self.SVMGridUnlocker, \
                       self.ui.cStopLineEdit: self.SVMGridUnlocker, \
                       self.ui.gStartLineEdit: self.SVMGridUnlocker, \
                       self.ui.gStepLineEdit: self.SVMGridUnlocker, \
                       self.ui.gStopLineEdit: self.SVMGridUnlocker, \
                       
                       self.ui.cValueLineEdit: self.SVMParametersUnlocker, \
                       self.ui.gValueLineEdit: self.SVMParametersUnlocker, \
                       
                       self.ui.saveSVMLineEdit: self.saveSVMUnlocker, \
                       
                       self.ui.loadSVMLineEdit: self.testingAndSVMUnlocker, \
                       self.ui.testingLoadFish1LineEdit: self.testingAndSVMUnlocker, \
                       self.ui.testingLoadFish2LineEdit: self.testingAndSVMUnlocker, \
                       }
        
        for field in self.Fields.keys():
            QtCore.QObject.connect(field, QtCore.SIGNAL('textChanged(QString)'), self.tryUnlock)
    
    def connectFileFields(self, handler):
        
        FileFields = [self.ui.loadTS1LineEdit, \
                           self.ui.loadTS2LineEdit, \
                           self.ui.saveSpikes1LineEdit, \
                           self.ui.saveSpikes2LineEdit, \
                           self.ui.saveWindowLengths1LineEdit, \
                           self.ui.saveWindowLengths2LineEdit, \
                           self.ui.loadSpikes1LineEdit, \
                           self.ui.loadSpikes2LineEdit, \
                           self.ui.saveFeatures1LineEdit, \
                           self.ui.saveFeatures2LineEdit, \
                           self.ui.saveFilterLineEdit, \
                           self.ui.saveRescaleLineEdit, \
                           self.ui.loadFeatures1LineEdit, \
                           self.ui.loadFeatures2LineEdit, \
                           self.ui.trainingSaveFish1LineEdit, \
                           self.ui.trainingSaveFish2LineEdit, \
                           self.ui.crossSaveFish1LineEdit, \
                           self.ui.crossSaveFish2LineEdit, \
                           self.ui.testingSaveFish1LineEdit, \
                           self.ui.testingSaveFish2LineEdit, \
                           self.ui.trainingLoadFish1LineEdit, \
                           self.ui.trainingLoadFish2LineEdit, \
                           self.ui.crossLoadFish1LineEdit, \
                           self.ui.crossLoadFish2LineEdit, \
                           self.ui.testingLoadFish1LineEdit, \
                           self.ui.testingLoadFish2LineEdit, \
                           self.ui.saveSVMLineEdit, \
                           self.ui.loadSVMLineEdit, \
                           ]
        
        for field in FileFields:
            QtCore.QObject.connect(field, QtCore.SIGNAL('clicked()'), self.fileFieldHandler)

    def verifyField(self, field):
        data = field.text()
        if self.fieldsType[field] == 'load':
            if os.path.isfile(data):
                return True
            else:
                return False
        elif self.fieldsType[field] == 'save':
            try:
                if os.path.isfile(data):
                    exists = True
                else:
                    exists = False
                open(data, 'a').close() # Nao destroi conteudo do arquivo
                if exists == False:
                    os.remove(data) # Nao cria um arquivo novo a menos que ja exista
                return True
            except:
                return False
            
        else:
            if data != '':
                return True
            else:
                return False
    
    def switchLockState(self, lockerList, state):
        for el in lockerList:
            el.setEnabled(state)
    
    def tryUnlock(self, text):
        field = self.sender()
        
        for tup in self.Fields[field]:
            allChecked = True
            for f in tup[0]:
                allChecked = allChecked and self.verifyField(f)
        
            self.switchLockState(tup[1], allChecked)
        
    
    def initialClickState(self):
        # Manually locks tesing line fields
        self.switchLockState(
            (self.ui.testingNumberSamplesFish1LineEdit, \
            self.ui.testingNumberSamplesFish2LineEdit, \
            self.ui.testingProbabilityFish1LineEdit, \
            self.ui.testingProbabilityFish2LineEdit
            ), \
            False)
        for tup in self.Fields.values():
            for locker,locked in tup:
                self.switchLockState(locked, False)

    def expandLayout(self):

        label = self.sender()
        idx = self.titleLabels.index(label)
        layout = self.ParametersLayout[idx]
        
        if self.isLayoutShown[idx]:
            label.setText( label.text()[:-2] + ' v' )
            if isinstance(layout, QtGui.QLayout):
                for i in xrange(layout.count()):
                    try:
                        layout.itemAt(i).widget().hide()
                    except:
                        pass
            elif isinstance(layout, QtGui.QWidget):
                layout.hide()
        
        else:
            label.setText( label.text()[:-2] + ' >' )
            if isinstance(layout, QtGui.QLayout):
                for i in xrange(layout.count()):
                    try:
                        layout.itemAt(i).widget().show()
                    except:
                        pass
            elif isinstance(layout, QtGui.QWidget):
                layout.show()

        self.isLayoutShown[idx] = not(self.isLayoutShown[idx])
        

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    myapp = TrainingWindow(app)

    myapp.show()
    sys.exit(app.exec_())
