import os, sys, inspect
import re

import numpy as np
import matplotlib.pyplot as plt

from PyQt4 import QtCore, QtGui
from training_interface import Ui_trainingWindow

# Default SVM values TODO: pegar de aquivo externo
defcStart = -5.0
defcStep = 2.0
defcStop = 15.0

defgStart = -15.0
defgStep = 2.0
defgStop = 3.0

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
        self.plotData, = self.ui.ROCWidget.canvas.ax.plot([],[],'k.')
        
        # LineFields List -> for saving parameters
        self.lineFieldsList = (self.ui.loadTS1LineEdit, \
                               self.ui.loadTS2LineEdit, \
                               self.ui.lowSaturation1LineEdit, \
                               self.ui.lowSaturation2LineEdit, \
                               self.ui.highSaturation1LineEdit, \
                               self.ui.highSaturation2LineEdit, \
                               self.ui.taps1LineEdit, \
                               self.ui.taps2LineEdit, \
                               self.ui.cutoff1LineEdit, \
                               self.ui.cutoff2LineEdit, \
                               self.ui.thresholdLevel1LineEdit, \
                               self.ui.thresholdLevel2LineEdit, \
                               self.ui.minlevel1LineEdit, \
                               self.ui.minlevel2LineEdit, \
                               self.ui.saveSpikes1LineEdit, \
                               self.ui.saveSpikes2LineEdit, \
                               self.ui.saveWindowLengths1LineEdit, \
                               self.ui.saveWindowLengths2LineEdit, \
                               self.ui.onlyAbove1LineEdit, \
                               self.ui.onlyAbove2LineEdit, \
                               self.ui.loadSpikes1LineEdit, \
                               self.ui.loadSpikes2LineEdit, \
                               self.ui.saveFeatures1LineEdit, \
                               self.ui.saveFeatures2LineEdit, \
                               self.ui.saveFilterLineEdit, \
                               self.ui.saveRescaleLineEdit, \
                               self.ui.loadFeatures1LineEdit, \
                               self.ui.loadFeatures2LineEdit, \
                               self.ui.trainingNumberSamplesFish1LineEdit, \
                               self.ui.trainingNumberSamplesFish2LineEdit, \
                               self.ui.trainingProbabilityFish1LineEdit, \
                               self.ui.trainingProbabilityFish2LineEdit, \
                               self.ui.trainingSaveFish1LineEdit, \
                               self.ui.trainingSaveFish2LineEdit, \
                               self.ui.trainingLoadFish1LineEdit, \
                               self.ui.trainingLoadFish2LineEdit, \
                               self.ui.crossNumberSamplesFish1LineEdit, \
                               self.ui.crossNumberSamplesFish2LineEdit, \
                               self.ui.crossProbabilityFish1LineEdit, \
                               self.ui.crossProbabilityFish2LineEdit, \
                               self.ui.crossSaveFish1LineEdit, \
                               self.ui.crossSaveFish2LineEdit, \
                               self.ui.crossLoadFish1LineEdit, \
                               self.ui.crossLoadFish2LineEdit, \
                               self.ui.testingNumberSamplesFish1LineEdit, \
                               self.ui.testingNumberSamplesFish2LineEdit, \
                               self.ui.testingProbabilityFish1LineEdit, \
                               self.ui.testingProbabilityFish2LineEdit, \
                               self.ui.testingSaveFish1LineEdit, \
                               self.ui.testingSaveFish2LineEdit, \
                               self.ui.testingLoadFish1LineEdit, \
                               self.ui.testingLoadFish2LineEdit, \
                               self.ui.cStartLineEdit, \
                               self.ui.cStepLineEdit, \
                               self.ui.cStopLineEdit, \
                               self.ui.cValueLineEdit, \
                               self.ui.gStartLineEdit, \
                               self.ui.gStepLineEdit, \
                               self.ui.gStopLineEdit, \
                               self.ui.gValueLineEdit, \
                               self.ui.saveSVMLineEdit, \
                               self.ui.loadSVMLineEdit, \
                               )
        
        # Program objects -> they must be parameters for the GarbageCollector
        # do not clean them
        self.filterAssist1Program = QtCore.QProcess()
        self.filterAssist2Program = QtCore.QProcess()
        self.thresholdAssist1Program = QtCore.QProcess()
        self.thresholdAssist2Program = QtCore.QProcess()
        self.minlevelAssist1Program = QtCore.QProcess()
        self.minlevelAssist2Program = QtCore.QProcess()
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
        self.svmtoolOptimProgram = QtCore.QProcess()
        self.svmtoolTrainProgram = QtCore.QProcess()
        self.svmtoolROCProgram = QtCore.QProcess()

        self.dicProgram = {'paramchooser lowpass': (self.filterAssist1Program, self.filterAssist2Program), \
                           'paramchooser threshold': (self.thresholdAssist1Program, self.thresholdAssist2Program, self.minlevelAssist1Program, self.minlevelAssist2Program), \
                           'winview': (self.verifySpikes1Program, self.verifySpikes2Program), \
                           'spikes Fish 1': (self.detectSpikes1Program, ), \
                           'spikes Fish 2': (self.detectSpikes2Program, ), \
                           'features compute': (self.featuresCompute1Program, self.featuresCompute2Program), \
                           'features rescale prepare': (self.featuresRescalePrepareProgram, ), \
                           'features rescale apply': (self.featuresRescaleApplyProgram, ), \
                           'features filter prepare': (self.featuresFilterPrepareProgram, ), \
                           'features filter apply': (self.featuresFilterApply1Program, self.featuresFilterApply2Program), \
                           'slice info': (self.sliceInfo1Program, self.sliceInfo2Program), \
                           'slice random': (self.sliceRandom1Program, self.sliceRandom2Program), \
                           'svmtool optim': (self.svmtoolOptimProgram, ), \
                           'svmtool train': (self.svmtoolTrainProgram, ), \
                           'svmtool roc': (self.svmtoolROCProgram, ), \
                           }
        
        self.cancelled = False
        self.finish1 = False
        self.finish2 = False

        self.ParametersLayout = (self.ui.step1ParametersLayout, \
                self.ui.step2ParametersLayout, \
                self.ui.step3ParametersLayout, \
                self.ui.tabWidget, \
                self.ui.step5ParametersLayout, \
                )

        self.titleLabels = (self.ui.step1TitleLabel, \
                self.ui.step2TitleLabel, \
                self.ui.step3TitleLabel, \
                self.ui.step4TitleLabel, \
                self.ui.step5TitleLabel, \
                )

        self.defineFieldsType()

        # Esconder campos do layout (deixar isLayoutShown = False, False, ...)
        # TODO: Pensar melhor de acordo com os lockers
        self.isLayoutShown = [True, \
        True, \
        True, \
        True, \
        True, \
        ]
        '''for layout in self.ParametersLayout:
            if isinstance(layout, QtGui.QLayout):
                for i in xrange(layout.count()):
                    try:
                        layout.itemAt(i).widget().hide()
                    except:
                        pass
            elif isinstance(layout, QtGui.QWidget):
                layout.hide()'''
        
        for label in self.titleLabels:
            QtCore.QObject.connect(label, QtCore.SIGNAL('clicked()'), self.expandLayout)
        
        # Connect load features file to load slice info
        QtCore.QObject.connect(self.ui.loadFeatures1LineEdit, QtCore.SIGNAL('textChanged(QString)'), self.sliceInfo)
        QtCore.QObject.connect(self.ui.loadFeatures2LineEdit, QtCore.SIGNAL('textChanged(QString)'), self.sliceInfo)
        
        # Connect cValue and gValue to warning window
        QtCore.QObject.connect(self.ui.cValueLineEdit, QtCore.SIGNAL('clicked()'), self.SVMValuesWarningWindow)
        QtCore.QObject.connect(self.ui.gValueLineEdit, QtCore.SIGNAL('clicked()'), self.SVMValuesWarningWindow)
        
        self.connectFileFields()
        self.connectUnlockFields()
        self.connectButtons()
        
        self.NWindows1 = 0.
        self.NWindows2 = 0.
        self.connectSliceFields()
        
        self.initialClickState()
    
    def saveParameters(self):
        saveFilename = QtGui.QFileDialog.getSaveFileName(self, 'Save Parameters File', '', 'Parameters File (*.trainparameters) (*.trainparameters);;All files (*.*) (*.*)')
        saveFile = open(saveFilename, 'w')
        for element in self.lineFieldsList:
            if isinstance(element, QtGui.QLineEdit):
                saveFile.write( '%s\t%s\n'%(element.objectName(), element.text()) )
        saveFile.close()

    def loadParameters(self):
        loadFilename = QtGui.QFileDialog.getOpenFileName(self, 'Load Parameters File', '', 'Parameters File (*.trainparameters) (*.trainparameters);;All files (*.*) (*.*)')
        loadFile = open(loadFilename, 'r')
        for line in loadFile.xreadlines():
            objectName, Value = line.split('\t')
            Value = Value.strip()
            if Value != '':
                for element in self.lineFieldsList:
                    if element.objectName() == objectName:
                        element.setText(Value)
                        break
    
    def connectButtons(self):
        QtCore.QObject.connect(self.ui.saveParametersBut, QtCore.SIGNAL('clicked()'), self.saveParameters)
        QtCore.QObject.connect(self.ui.loadParametersBut, QtCore.SIGNAL('clicked()'), self.loadParameters)
        
        QtCore.QObject.connect(self.ui.filterAssist1But, QtCore.SIGNAL('clicked()'), self.filterAssist1)
        QtCore.QObject.connect(self.ui.filterAssist2But, QtCore.SIGNAL('clicked()'), self.filterAssist2)
        
        QtCore.QObject.connect(self.ui.thresholdAssist1But, QtCore.SIGNAL('clicked()'), self.thresholdAssist1)
        QtCore.QObject.connect(self.ui.thresholdAssist2But, QtCore.SIGNAL('clicked()'), self.thresholdAssist2)
        
        QtCore.QObject.connect(self.ui.minlevel1But, QtCore.SIGNAL('clicked()'), self.minlevelAssist1)
        QtCore.QObject.connect(self.ui.minlevel2But, QtCore.SIGNAL('clicked()'), self.minlevelAssist2)
        
        QtCore.QObject.connect(self.ui.verifySpikes1But, QtCore.SIGNAL('clicked()'), self.verifySpikes1)
        QtCore.QObject.connect(self.ui.verifySpikes2But, QtCore.SIGNAL('clicked()'), self.verifySpikes2)
        
        QtCore.QObject.connect(self.ui.detectSpikes1But, QtCore.SIGNAL('clicked()'), self.detectSpikes1)
        QtCore.QObject.connect(self.ui.detectSpikes2But, QtCore.SIGNAL('clicked()'), self.detectSpikes2)
        
        QtCore.QObject.connect(self.ui.extractFeaturesBut, QtCore.SIGNAL('clicked()'), self.extractFeatures)
        
        QtCore.QObject.connect(self.ui.sliceFish1But, QtCore.SIGNAL('clicked()'), self.sliceRandom1)
        QtCore.QObject.connect(self.ui.sliceFish2But, QtCore.SIGNAL('clicked()'), self.sliceRandom2)
        
        QtCore.QObject.connect(self.ui.defaultSVMValuesBut, QtCore.SIGNAL('clicked()'), self.defaultSVMValues)
        
        QtCore.QObject.connect(self.ui.optimizeSVMBut, QtCore.SIGNAL('clicked()'), self.SVMToolOptim)
        
        QtCore.QObject.connect(self.ui.trainSVMBut, QtCore.SIGNAL('clicked()'), self.SVMToolTrain)
        
        QtCore.QObject.connect(self.ui.generateROCBut, QtCore.SIGNAL('clicked()'), self.generateROC)
    
    def isReturnCodeOk(self, ret):
        if ret != 0:
            print '\n---\tERROR (%s): %d\t---\n'%(self.programname, ret)
            for program in self.dicProgram[self.programname]:
                print program.readAllStandardOutput()
                print program.readAllStandardError()
            self.raiseParameterError('%s ERROR!\n'%self.programname)
            return False
        else:
            return True
    
    def printAllStandardOutput(self):
        print 'stdout:%s\n'%self.programname
        for program in self.dicProgram[self.programname]:
            print(program.readAllStandardOutput())
    
    def printAllStandardError(self):
        print 'stderr:%s\n'%self.programname
        for program in self.dicProgram[self.programname]:
            print(program.readAllStandardError())
    
    def filterAssist1(self):
        print 'paramchooser lowpass 1'
        TSName = self.ui.loadTS1LineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'paramchooser lowpass'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.filterAssist1Program.start('./../paramchooser/paramchooser', ['lowpass', TSName])
        
        self.cancelled = False
        def filterAssist1Finish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                out = self.filterAssist1Program.readAllStandardOutput()
                out = out + '\n' + self.filterAssist1Program.readAllStandardError()
                
                out = str(out)
                
                numtaps = out.split('numtaps = ')[1].split('\n')[0]
                cutoff = out.split('cutoff = ')[1].split('\n')[0]
                
                self.ui.taps1LineEdit.setText(numtaps)
                self.ui.cutoff1LineEdit.setText(cutoff)
            else:
                return None
        
        QtCore.QObject.connect(self.filterAssist1Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), filterAssist1Finish)
        
    def filterAssist2(self):
        print 'paramchooser lowpass 2'
        TSName = self.ui.loadTS2LineEdit.text()
       
        # Same name of self.dicProgram
        self.programname = 'paramchooser lowpass'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.filterAssist2Program.start('./../paramchooser/paramchooser', ['lowpass', TSName])
        
        self.cancelled = False
        def filterAssist2Finish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                out = self.filterAssist2Program.readAllStandardOutput()
                out = out + '\n' + self.filterAssist2Program.readAllStandardError()
                
                out = str(out)
                
                numtaps = out.split('numtaps = ')[1].split('\n')[0]
                cutoff = out.split('cutoff = ')[1].split('\n')[0]
                
                self.ui.taps2LineEdit.setText(numtaps)
                self.ui.cutoff2LineEdit.setText(cutoff)
            else:
                return None
        
        QtCore.QObject.connect(self.filterAssist2Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), filterAssist2Finish)
    
    def thresholdAssist1(self):
        print 'paramchooser threshold 1'
        TSName = self.ui.loadTS1LineEdit.text()
        taps = self.ui.taps1LineEdit.text()
        cutoff = self.ui.cutoff1LineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'paramchooser threshold'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )        
        self.thresholdAssist1Program.start('./../paramchooser/paramchooser', ['threshold', TSName, taps, cutoff])
        
        self.cancelled = False
        def thresholdAssist1Finish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                out = self.thresholdAssist1Program.readAllStandardOutput()
                out = out + '\n' + self.thresholdAssist1Program.readAllStandardError()
                
                out = str(out)
                
                threshold = out.split('threshold = ')[1].split('\n')[0]
                self.ui.thresholdLevel1LineEdit.setText(threshold)
            else:
                return None
        
        QtCore.QObject.connect(self.thresholdAssist1Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), thresholdAssist1Finish)
        
    
    def thresholdAssist2(self):
        print 'paramchooser threshold 2'
        TSName = self.ui.loadTS2LineEdit.text()
        taps = self.ui.taps2LineEdit.text()
        cutoff = self.ui.cutoff2LineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'paramchooser threshold'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )        
        self.thresholdAssist2Program.start('./../paramchooser/paramchooser', ['threshold', TSName, taps, cutoff])
        
        self.cancelled = False
        def thresholdAssist2Finish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                out = self.thresholdAssist2Program.readAllStandardOutput()
                out = out + '\n' + self.thresholdAssist2Program.readAllStandardError()
                
                out = str(out)
                
                threshold = out.split('threshold = ')[1].split('\n')[0]
                self.ui.thresholdLevel2LineEdit.setText(threshold)
            else:
                return None
        
        QtCore.QObject.connect(self.thresholdAssist2Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), thresholdAssist2Finish)
    
    def minlevelAssist1(self):
        print 'paramchooser threshold 1'
        TSName = self.ui.loadTS1LineEdit.text()
        taps = self.ui.taps1LineEdit.text()
        cutoff = self.ui.cutoff1LineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'paramchooser threshold'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.minlevelAssist1Program.start('./../paramchooser/paramchooser', ['threshold', TSName, taps, cutoff])
        
        self.cancelled = False
        def minlevelAssist1Finish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                out = self.minlevelAssist1Program.readAllStandardOutput()
                out = out + '\n' + self.minlevelAssist1Program.readAllStandardError()
                
                out = str(out)
                
                threshold = out.split('threshold = ')[1].split('\n')[0]
                self.ui.minlevel1LineEdit.setText(threshold)
            else:
                return None
        
        QtCore.QObject.connect(self.minlevelAssist1Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), minlevelAssist1Finish)
    
    def minlevelAssist2(self):
        print 'paramchooser threshold 2'
        TSName = self.ui.loadTS2LineEdit.text()
        taps = self.ui.taps2LineEdit.text()
        cutoff = self.ui.cutoff2LineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'paramchooser threshold'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.minlevelAssist2Program.start('./../paramchooser/paramchooser', ['threshold', TSName, taps, cutoff])
        
        self.cancelled = False
        def minlevelAssist2Finish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                out = self.minlevelAssist2Program.readAllStandardOutput()
                out = out + '\n' + self.minlevelAssist2Program.readAllStandardError()
                
                out = str(out)
                
                threshold = out.split('threshold = ')[1].split('\n')[0]
                self.ui.minlevel2LineEdit.setText(threshold)
            else:
                return None
        
        QtCore.QObject.connect(self.minlevelAssist2Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), minlevelAssist2Finish)
    
    def verifySpikes1(self):
        print 'winview 1'
        spikesName = self.ui.loadSpikes1LineEdit.text()
        TSName = self.ui.loadTS1LineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'winview'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        if TSName != '':
            self.verifySpikes1Program.start('./../winview/winview', [spikesName, TSName])
        else:
            self.verifySpikes1Program.start('./../winview/winview', [spikesName])
        
        self.cancelled = False
        def verifySpikes1Finish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                pass
            else:
                return None
            
        QtCore.QObject.connect(self.verifySpikes1Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), verifySpikes1Finish)
        
    def verifySpikes2(self):
        print 'winview 2'
        spikesName = self.ui.loadSpikes2LineEdit.text()
        TSName = self.ui.loadTS2LineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'winview'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        if TSName != '':
            self.verifySpikes2Program.start('./../winview/winview', [spikesName, TSName])
        else:
            self.verifySpikes2Program.start('./../winview/winview', [spikesName])
        
        self.cancelled = False
        def verifySpikes2Finish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                pass
            else:
                return None
            
        QtCore.QObject.connect(self.verifySpikes2Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), verifySpikes2Finish)
    
    def detectSpikes1(self):
        print 'spikes 1'
        TSName = self.ui.loadTS1LineEdit.text()
        lowSat = self.ui.lowSaturation1LineEdit.text()
        highSat = self.ui.highSaturation1LineEdit.text()
        taps = self.ui.taps1LineEdit.text()
        cutoff = self.ui.cutoff1LineEdit.text()
        threshold = self.ui.thresholdLevel1LineEdit.text()
        saveSpikes = self.ui.saveSpikes1LineEdit.text()
        onlyAbove = self.ui.onlyAbove1LineEdit.text()
        
        dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        # Same name of self.dicProgram
        self.programname = 'spikes Fish 1'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.detectSpikes1Program.start('./../spikes/spikes', \
                           ['--fixedwin', \
                            '--useHilbert', \
                            '--detection=%s'%(threshold), \
############################'--refractory=%s'%(refractory), \
############################'--max_size=%s'%(maxSize), \
                            '--saturation=%s,%s'%(lowSat,highSat), \
                            '--numtaps=%s'%taps, \
                            '--cutoff=%s'%cutoff, \
                            '--detection=%s'%threshold, \
                            '--onlyabove=%s'%onlyAbove, \
                            TSName, \
                            saveSpikes])
        
        self.cancelled = False
        def detectSpikes1Finish(ret, exitStatus):
            self.app.restoreOverrideCursor()
            dialog.hide()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.ui.loadSpikes1LineEdit.setText(saveSpikes)
            else:
                return None
            
        QtCore.QObject.connect(self.detectSpikes1Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), detectSpikes1Finish)
        QtCore.QObject.connect(self.detectSpikes1Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.detectSpikes1Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
        
    def detectSpikes2(self):
        print 'spikes 2'
        TSName = self.ui.loadTS2LineEdit.text()
        lowSat = self.ui.lowSaturation2LineEdit.text()
        highSat = self.ui.highSaturation2LineEdit.text()
        taps = self.ui.taps2LineEdit.text()
        cutoff = self.ui.cutoff2LineEdit.text()
        threshold = self.ui.thresholdLevel2LineEdit.text()
        saveSpikes = self.ui.saveSpikes2LineEdit.text()
        saveWindowLengths = self.ui.saveWindowLengths2LineEdit.text()
        onlyAbove = self.ui.onlyAbove2LineEdit.text()
        minlevel = self.ui.minlevel2LineEdit.text()
        
        dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        # Same name of self.dicProgram
        self.programname = 'spikes Fish 2'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.detectSpikes2Program.start('./../spikes/spikes', \
                           ['--fixedwin', \
                            '--useHilbert', \
                            '--detection=%s'%(threshold), \
############################'--refractory=%s'%(refractory), \
############################'--max_size=%s'%(maxSize), \
                            '--saturation=%s,%s'%(lowSat,highSat), \
                            '--numtaps=%s'%taps, \
                            '--cutoff=%s'%cutoff, \
                            '--detection=%s'%threshold, \
                            '--onlyabove=%s'%onlyAbove, \
                            TSName, \
                            saveSpikes])
        
        self.cancelled = False
        def detectSpikes2Finish(ret, exitStatus):
            self.app.restoreOverrideCursor()
            dialog.hide()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.ui.loadSpikes2LineEdit.setText(saveSpikes)
            else:
                return None
            
        QtCore.QObject.connect(self.detectSpikes2Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), detectSpikes2Finish)
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
        
        # Will call the other functions sequentially using listeners
        self.featuresCompute() 
        
    def featuresCompute(self):
        print 'features compute'
        
        # Same name of self.dicProgram
        self.programname = 'features compute'
        
        self.finish1 = False
        self.finish2 = False
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.featuresCompute1Program.start('./../features/features', \
                           ['compute', \
                            self.spikesName1, \
                            self.unfilteredFeaturesName1])
        
        self.featuresCompute2Program.start('./../features/features', \
                           ['compute', \
                            self.spikesName2, \
                            self.unfilteredFeaturesName2])
        
        self.cancelled = False
        def featuresComputeFinish(ret, exitStatus):
            sender = self.sender()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                if sender == self.featuresCompute1Program:
                    self.finish1 = True
                elif sender == self.featuresCompute2Program:
                    self.finish2 = True
                if self.finish1 == True and self.finish2 == True:
                    self.finish1 = False
                    self.finish2 = False
                    self.featuresRescalePrepare()
            else:
                self.finish1 = False
                self.finish2 = False
                if os.path.isfile(self.unfilteredFeaturesName1):
                    os.remove(self.unfilteredFeaturesName1)
                if os.path.isfile(self.unfilteredFeaturesName2):
                    os.remove(self.unfilteredFeaturesName2)
                self.app.restoreOverrideCursor()
                self.dialog.hide()
        
        QtCore.QObject.connect(self.featuresCompute1Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), featuresComputeFinish)
        QtCore.QObject.connect(self.featuresCompute2Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), featuresComputeFinish)
        QtCore.QObject.connect(self.featuresCompute1Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresCompute2Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresCompute1Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        QtCore.QObject.connect(self.featuresCompute2Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
    def featuresRescalePrepare(self):        
        print 'features rescale prepare'
        
        # Same name of self.dicProgram
        self.programname = 'features rescale prepare'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.featuresRescalePrepareProgram.start('./../features/features', \
                           ['rescale', \
                            'prepare', \
                            self.rescaleName, \
                            self.unfilteredFeaturesName1, \
                            self.unfilteredFeaturesName2])
        
        self.cancelled = False
        def featuresRescalePrepareFinish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.featuresRescaleApply()
            else:
                if os.path.isfile(self.unfilteredFeaturesName1):
                    os.remove(self.unfilteredFeaturesName1)
                if os.path.isfile(self.unfilteredFeaturesName2):
                    os.remove(self.unfilteredFeaturesName2)
                self.app.restoreOverrideCursor()
                self.dialog.hide()
                
        QtCore.QObject.connect(self.featuresRescalePrepareProgram, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), featuresRescalePrepareFinish)
        QtCore.QObject.connect(self.featuresRescalePrepareProgram, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresRescalePrepareProgram, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
    def featuresRescaleApply(self):
        print 'features rescale apply'
        
        # Same name of self.dicProgram
        self.programname = 'features rescale apply'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.featuresRescaleApplyProgram.start('./../features/features', \
                           ['rescale', \
                            'apply', \
                            self.rescaleName, \
                            self.unfilteredFeaturesName1, \
                            self.unfilteredFeaturesName2])
        
        self.cancelled = False
        def featuresRescaleApplyFinish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.featuresFilterPrepare()
            else:
                if os.path.isfile(self.unfilteredFeaturesName1):
                    os.remove(self.unfilteredFeaturesName1)
                if os.path.isfile(self.unfilteredFeaturesName2):
                    os.remove(self.unfilteredFeaturesName2)
                self.app.restoreOverrideCursor()
                self.dialog.hide()
        
        QtCore.QObject.connect(self.featuresRescaleApplyProgram, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), featuresRescaleApplyFinish)
        QtCore.QObject.connect(self.featuresRescaleApplyProgram, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresRescaleApplyProgram, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
    def featuresFilterPrepare(self):
        print 'features filter prepare'
        
        # Same name of self.dicProgram
        self.programname = 'features filter prepare'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.featuresFilterPrepareProgram.start('./../features/features', \
                           ['filter', \
                            'prepare', \
                            '--best=%s'%self.number, \
                            '--hist-bars=40', \
                            self.filterName, \
                            self.unfilteredFeaturesName1, \
                            self.unfilteredFeaturesName2])
        
        self.cancelled = False
        def featuresFilterPrepareFinish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.featuresFilterApply()
            else:
                if os.path.isfile(self.unfilteredFeaturesName1):
                    os.remove(self.unfilteredFeaturesName1)
                if os.path.isfile(self.unfilteredFeaturesName2):
                    os.remove(self.unfilteredFeaturesName2)
                self.app.restoreOverrideCursor()
                self.dialog.hide()
                
        QtCore.QObject.connect(self.featuresFilterPrepareProgram, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), featuresFilterPrepareFinish)
        QtCore.QObject.connect(self.featuresFilterPrepareProgram, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresFilterPrepareProgram, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
        
    def featuresFilterApply(self):
        print 'features filter apply'
        
        # Same name of self.dicProgram
        self.programname = 'features filter apply'
        
        self.finish1 = False
        self.finish2 = False
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.featuresFilterApply1Program.start('./../features/features', \
                           ['filter', \
                            'apply', \
                            self.filterName, \
                            self.unfilteredFeaturesName1, \
                            self.featuresName1])
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.featuresFilterApply2Program.start('./../features/features', \
                           ['filter', \
                            'apply', \
                            self.filterName, \
                            self.unfilteredFeaturesName2, \
                            self.featuresName2])
        
        self.cancelled = False
        def featuresFilterApplyFinish(ret, exitStatus):
            sender = self.sender()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                if sender == self.featuresFilterApply1Program:
                    self.finish1 = True
                elif sender == self.featuresFilterApply2Program:
                    self.finish2 = True
                if self.finish1 == True and self.finish2 == True:
                    self.finish1 = False
                    self.finish2 = False
                    self.featuresFinish()
            else:
                self.finish1 = False
                self.finish2 = False
                if os.path.isfile(self.unfilteredFeaturesName1):
                    os.remove(self.unfilteredFeaturesName1)
                if os.path.isfile(self.unfilteredFeaturesName2):
                    os.remove(self.unfilteredFeaturesName2)
                self.app.restoreOverrideCursor()
                self.dialog.hide()
        
        QtCore.QObject.connect(self.featuresFilterApply1Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), featuresFilterApplyFinish)
        QtCore.QObject.connect(self.featuresFilterApply2Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), featuresFilterApplyFinish)
        QtCore.QObject.connect(self.featuresFilterApply1Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresFilterApply2Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.featuresFilterApply1Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        QtCore.QObject.connect(self.featuresFilterApply2Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
    def featuresFinish(self):
        print 'end features'
        self.ui.loadFeatures1LineEdit.setText(self.featuresName1)
        self.ui.loadFeatures2LineEdit.setText(self.featuresName2)
        if os.path.isfile(self.unfilteredFeaturesName1):
            os.remove(self.unfilteredFeaturesName1)
        if os.path.isfile(self.unfilteredFeaturesName2):
            os.remove(self.unfilteredFeaturesName2)
        self.app.restoreOverrideCursor()
        self.dialog.hide()
    
    def sliceInfo(self, filename):
        print 'slice info'
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        field = self.sender()
        featuresName = field.text()
        
        def fillInfoLabel1(ret, exitStatus):
            self.app.restoreOverrideCursor()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit):
                stdout = self.sliceInfo1Program.readAllStandardOutput()
                stderr = self.sliceInfo1Program.readAllStandardError()
                if stdout != '':
                    text, self.NWindows1 = self.formatInfoText(str(stdout))
                else:
                    text, self.NWindows1 = self.formatInfoText(str(stderr))
                self.ui.sliceInfoFish1Label.setText(text)
            else:
                return None
        
        def fillInfoLabel2(ret, exitStatus):
            self.app.restoreOverrideCursor()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit):
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
            #Be sure that is on current directory
            os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
            if field == self.ui.loadFeatures1LineEdit:
                self.sliceInfo1Program.start('./../slice/slice', \
                                             ['info', \
                                              featuresName])
                QtCore.QObject.connect(self.sliceInfo1Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), fillInfoLabel1)
            else:
                self.sliceInfo2Program.start('./../slice/slice', \
                                             ['info', \
                                              featuresName])
                QtCore.QObject.connect(self.sliceInfo2Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), fillInfoLabel2)
   
    def sliceRandom1(self):
        featuresName = self.ui.loadFeatures1LineEdit.text()
        probTrain = float(self.ui.trainingProbabilityFish1LineEdit.text())
        saveTrain = self.ui.trainingSaveFish1LineEdit.text()
        probCross = float(self.ui.crossProbabilityFish1LineEdit.text())
        saveCross = self.ui.crossSaveFish1LineEdit.text()
        probTest = float(self.ui.testingProbabilityFish1LineEdit.text())
        saveTest = self.ui.testingSaveFish1LineEdit.text()
        
        if (0 < probTrain < 1.0) and \
           (0 < probCross < 1.0) and \
           (0 < probTest < 1.0) and \
           (0 <= probTrain + probCross + probTest <= 1.0):
            print 'slice random'
            self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            
            self.programname = 'slice random'
            #Be sure that is on current directory
            os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
            self.sliceRandom1Program.start('./../slice/slice', \
                                           ['random', \
                                            featuresName, \
                                            str(probTrain), saveTrain, \
                                            str(probCross), saveCross, \
                                            str(probTest), saveTest])
            
            def sliceRandomFinish(ret, exitStatus):
                self.app.restoreOverrideCursor()
                if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit):
                    self.ui.trainingLoadFish1LineEdit.setText(self.ui.trainingSaveFish1LineEdit.text())
                    self.ui.crossLoadFish1LineEdit.setText(self.ui.crossSaveFish1LineEdit.text())
                    self.ui.testingLoadFish1LineEdit.setText(self.ui.testingSaveFish1LineEdit.text())
            
            QtCore.QObject.connect(self.sliceRandom1Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), sliceRandomFinish)
            QtCore.QObject.connect(self.sliceRandom1Program, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
            QtCore.QObject.connect(self.sliceRandom1Program, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        else:
            QtGui.QMessageBox.critical(self, "ERROR", 'Please check your parameters!\nAll the probabilities must be on the interval (0,1), and their sum on the interval [0,1]', QtGui.QMessageBox.Ok)
    
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
            
            self.programname = 'slice random'
            #Be sure that is on current directory
            os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
            self.sliceRandom2Program.start('./../slice/slice', \
                                           ['random', \
                                            featuresName, \
                                            str(probTrain), saveTrain, \
                                            str(probCross), saveCross, \
                                            str(probTest), saveTest])
            
            def sliceRandomFinish(ret, exitStatus):
                self.app.restoreOverrideCursor()
                if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit):
                    self.ui.trainingLoadFish2LineEdit.setText(self.ui.trainingSaveFish2LineEdit.text())
                    self.ui.crossLoadFish2LineEdit.setText(self.ui.crossSaveFish2LineEdit.text())
                    self.ui.testingLoadFish2LineEdit.setText(self.ui.testingSaveFish2LineEdit.text())
            
            QtCore.QObject.connect(self.sliceRandom2Program, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), sliceRandomFinish)
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
            filename = QtGui.QFileDialog.getSaveFileName(self, 'Save file', path, fileFilter )
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
        print 'Cancelled.'
        self.cancelled = True
        self.app.restoreOverrideCursor()
        for l in self.dicProgram.values():
            for program in l:
                program.close()
    
    def defineFieldsType(self):
        self.fieldsType = {self.ui.loadTS1LineEdit: 'load', \
                       
                       self.ui.loadTS2LineEdit: 'load', \
                       
                       self.ui.lowSaturation1LineEdit: 'float', \
                       self.ui.highSaturation1LineEdit: 'float', \
                       self.ui.taps1LineEdit: 'int', \
                       self.ui.cutoff1LineEdit: 'float', \
                       self.ui.thresholdLevel1LineEdit: 'float', \
                       self.ui.minlevel1LineEdit: 'float', \
                       
                       self.ui.lowSaturation2LineEdit: 'float', \
                       self.ui.highSaturation2LineEdit: 'float', \
                       self.ui.taps2LineEdit: 'int', \
                       self.ui.cutoff2LineEdit: 'float', \
                       self.ui.thresholdLevel2LineEdit: 'float', \
                       self.ui.minlevel2LineEdit: 'float', \
                       
                       self.ui.saveSpikes1LineEdit: 'save', \
                       self.ui.saveWindowLengths1LineEdit: 'save', \
                       self.ui.onlyAbove1LineEdit: 'float', \
                       
                       self.ui.saveSpikes2LineEdit: 'save', \
                       self.ui.saveWindowLengths2LineEdit: 'save', \
                       self.ui.onlyAbove2LineEdit: 'float', \
                       
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
                prob = np.floor(1e6*(float(text) / float(self.NWindows1)))/1e6
            else:
                prob = np.floor(1e6*(float(text) / float(self.NWindows2)))/1e6
            
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
                trainingProb = self.ui.trainingProbabilityFish1LineEdit.text()
                crossProb = self.ui.crossProbabilityFish1LineEdit.text()
                outField = self.ui.testingProbabilityFish1LineEdit
            else:
                trainingProb = self.ui.trainingProbabilityFish2LineEdit.text()
                crossProb = self.ui.crossProbabilityFish2LineEdit.text()
                outField = self.ui.testingProbabilityFish2LineEdit
            
            if trainingProb == '' or crossProb == '':
                outField.setText('')
                return None
            
            output = str( np.floor(1e6*(1 - (float(trainingProb) + float(crossProb))))/1e6 )
            outField.setText(output)
            
        for field in self.testingDependency:
            QtCore.QObject.connect(field, QtCore.SIGNAL('textChanged(QString)'), updateTesting)
        
    
    def defaultSVMValues(self):
        self.ui.cStartLineEdit.setText(str(defcStart))
        self.ui.cStopLineEdit.setText(str(defcStop))
        self.ui.cStepLineEdit.setText(str(defcStep))
        
        self.ui.gStartLineEdit.setText(str(defgStart))
        self.ui.gStopLineEdit.setText(str(defgStop))
        self.ui.gStepLineEdit.setText(str(defgStep))
    
    def SVMValuesWarningWindow(self):
        field = self.sender()
        
        if field.text() == '':
            QtGui.QMessageBox.critical(self, "WARNING", 'We recommend that you optimize the parameters instead of selecting them directly.\n' + 
                                       'If you with the select them directly, do it at your own risk.', QtGui.QMessageBox.Ok)
    
    def SVMToolOptim(self):
        train1Name = self.ui.trainingLoadFish1LineEdit.text()
        train2Name = self.ui.trainingLoadFish2LineEdit.text()
        cross1Name = self.ui.crossLoadFish1LineEdit.text()
        cross2Name = self.ui.crossLoadFish2LineEdit.text()
        
        cStart = self.ui.cStartLineEdit.text()
        cStop = self.ui.cStopLineEdit.text()
        cStep = self.ui.cStepLineEdit.text()
        
        gStart = self.ui.gStartLineEdit.text()
        gStop = self.ui.gStopLineEdit.text()
        gStep = self.ui.gStepLineEdit.text()
        
        if cStart == '' or \
           cStop == '' or \
           cStep == '' or \
           gStart == '' or \
           gStop == '' or \
           gStep == '':
            QtGui.QMessageBox.critical(self, "ERROR", 'Please complete all Start, Stop, Step value to optimize parameters\n(Or click on the default values)', QtGui.QMessageBox.Ok)
            return None
        
        if float(cStop) <= float(cStart) or \
           float(gStop) <= float(gStart):
            QtGui.QMessageBox.critical(self, "ERROR", 'cStop and gStop must be greater than cStart and gStart ', QtGui.QMessageBox.Ok)
            return None
        
        if float(cStep) <= 0 or \
           float(gStep) <= 0:
            QtGui.QMessageBox.critical(self, "ERROR", 'cStep and gStep must be greater than 0', QtGui.QMessageBox.Ok)
            return None
        
        dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        self.svmOutput = ''
        
        # Same name of self.dicProgram
        self.programname = 'svmtool optim'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )

        self.f = open('output.txt','w')

        self.svmtoolOptimProgram.start('./../svmtool/svmtool', \
                                       ['optim', \
                                        '-c %s,%s,%s'%(cStart,cStop,cStep), \
                                        '-g %s,%s,%s'%(gStart,gStop,gStep), \
                                        train1Name, \
                                        train2Name, \
                                        cross1Name, \
                                        cross2Name, \
                                         ])
        
        def getOuput():
            stdout = self.svmtoolOptimProgram.readAllStandardOutput()
            self.svmOutput = self.svmOutput + stdout
            if stdout != '':
                print 'stdout:\t%s'%str(stdout).strip()
                self.f.write(str(stdout).strip()+'\n')
            stderr = self.svmtoolOptimProgram.readAllStandardError()
            self.svmOutput = self.svmOutput + stderr
            if stderr != '':
                print 'stderr:\t%s'%str(stderr).strip()
                self.f.write(str(stderr).strip()+'\n')
            self.f.flush()
        
        self.cancelled = False
        def svmtoolOptimFinish(ret, exitStatus):
            self.app.restoreOverrideCursor()
            dialog.hide()
            self.f.close()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                
                stdout = self.svmtoolOptimProgram.readAllStandardOutput()
                self.svmOutput = self.svmOutput + stdout
                stderr = self.svmtoolOptimProgram.readAllStandardError()
                self.svmOutput = self.svmOutput + stderr
                
                parse = re.search('(.*)Best: c=(.*), g=(.*)\n(.*)', self.svmOutput)
                self.ui.cValueLineEdit.setText(str(parse.group(2)))
                self.ui.gValueLineEdit.setText(str(parse.group(3)))
            else:
                return None
        
        QtCore.QObject.connect(self.svmtoolOptimProgram, QtCore.SIGNAL('readyReadStandardOutput()'), getOuput)
        QtCore.QObject.connect(self.svmtoolOptimProgram, QtCore.SIGNAL('readyReadStandardError()'), getOuput)
        QtCore.QObject.connect(self.svmtoolOptimProgram, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), svmtoolOptimFinish)
        
    def SVMToolTrain(self):
        SVMModelName = self.ui.saveSVMLineEdit.text()
        cValue = self.ui.cValueLineEdit.text()
        gValue = self.ui.gValueLineEdit.text()
        train1Name = self.ui.trainingLoadFish1LineEdit.text()
        train2Name = self.ui.trainingLoadFish2LineEdit.text()
        
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        # Same name of self.dicProgram
        self.programname = 'svmtool train'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.svmtoolTrainProgram.start('./../svmtool/svmtool', \
                                       ['train', \
                                        SVMModelName, \
                                        cValue, \
                                        gValue, \
                                        train1Name, \
                                        train2Name])
        
        self.cancelled = False
        def SVMToolTrainFinish(ret, exitStatus):
            self.app.restoreOverrideCursor()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.ui.loadSVMLineEdit.setText(self.ui.saveSVMLineEdit.text())
            else:
                return None
        
        QtCore.QObject.connect(self.svmtoolTrainProgram, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), SVMToolTrainFinish)
        QtCore.QObject.connect(self.svmtoolTrainProgram, QtCore.SIGNAL('readyReadStandardOutput()'),self.printAllStandardOutput)
        QtCore.QObject.connect(self.svmtoolTrainProgram, QtCore.SIGNAL('readyReadStandardError()'),self.printAllStandardError)
    
    def generateROC(self):
        self.svmModelName = self.ui.loadSVMLineEdit.text()
        self.testingName1 = self.ui.testingLoadFish1LineEdit.text()
        self.testingName2 = self.ui.testingLoadFish2LineEdit.text()
        
        self.dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        # Will call the other functions sequentially using listeners
        self.SVMToolROC()
    
    def SVMToolROC(self):
        print 'svmtool roc'
        
        self.svmOutput = ''
        self.FalsePositive = []
        self.TruePositive = []
        
        # Same name of self.dicProgram
        self.programname = 'svmtool roc'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.svmtoolROCProgram.start('./../svmtool/svmtool', \
                                       ['roc', \
                                       self.svmModelName, \
                                       self.testingName1, \
                                       self.testingName2])
        
        def getOutput():
            stdout = self.svmtoolROCProgram.readAllStandardOutput()
            self.svmOutput = self.svmOutput + stdout
            if stdout != '':
                print 'stdout:\t%s'%str(stdout).strip()
            stderr = self.svmtoolROCProgram.readAllStandardError()
            self.svmOutput = self.svmOutput + stderr
            if stderr != '':
                print 'stderr:\t%s'%str(stderr).strip()
        
        self.cancelled = False
        def svmtoolROCFinish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                stdout = self.svmtoolROCProgram.readAllStandardOutput()
                self.svmOutput = self.svmOutput + stdout
                stderr = self.svmtoolROCProgram.readAllStandardError()
                self.svmOutput = self.svmOutput + stderr
                
                ROCList = self.svmOutput.split('\n')
                Tam = len(ROCList)
                self.FalsePositive = np.zeros(Tam)
                self.TruePositive = np.zeros(Tam)
                
                # [:-1] to take off empty string from the last '\n'
                for n,tup in enumerate(ROCList[:-1]):
                    self.FalsePositive[n] = float(tup.split(' ')[0])
                    self.TruePositive[n] = float(tup.split(' ')[1])
                
                self.plotROC()
            else:
                return None
        
        QtCore.QObject.connect(self.svmtoolROCProgram, QtCore.SIGNAL('readyReadStandardOutput()'), getOutput)
        QtCore.QObject.connect(self.svmtoolROCProgram, QtCore.SIGNAL('readyReadStandardError()'), getOutput)
        QtCore.QObject.connect(self.svmtoolROCProgram, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), svmtoolROCFinish)
    
    def plotROC(self):
        f = plt.figure(1, figsize=(10,10))
        ax = f.add_subplot(111)
        ax.plot(self.FalsePositive, self.TruePositive)
        plt.show()
        
        self.plotData.set_xdata(self.FalsePositive)
        self.plotData.set_ydata(self.TruePositive)
        self.ax.axis([0., 1., 0., 1.])
        self.ax.grid()
        self.fig.canvas.draw()
        
        self.dialog.hide()
        self.app.restoreOverrideCursor()
    
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
                 self.ui.minlevel1LineEdit, \
                 ), \
                (self.ui.saveSpikes1LineEdit, \
                 self.ui.saveWindowLengths1LineEdit, \
                 self.ui.onlyAbove1LineEdit, \
                ) \
            ), \
            ( \
                (self.ui.taps1LineEdit, \
                 self.ui.cutoff1LineEdit, \
                 ), \
                (self.ui.thresholdAssist1But, \
                 self.ui.thresholdLevel1LineEdit, \
                 self.ui.minlevel1But, \
                 self.ui.minlevel1LineEdit, \
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
                 self.ui.minlevel2LineEdit, \
                 ), \
                (self.ui.saveSpikes2LineEdit, \
                 self.ui.saveWindowLengths2LineEdit, \
                 self.ui.onlyAbove2LineEdit, \
                ) \
            ), \
            ( \
                (self.ui.taps2LineEdit, \
                 self.ui.cutoff2LineEdit, \
                 ), \
                (self.ui.thresholdAssist2But, \
                 self.ui.thresholdLevel2LineEdit, \
                 self.ui.minlevel2But, \
                 self.ui.minlevel2LineEdit, \
                 ) \
            ), \
        )
        
        self.spikeSavefilesFish1Unlocker = ( \
            ( \
                (self.ui.saveSpikes1LineEdit, \
                 self.ui.saveWindowLengths1LineEdit, \
                 self.ui.onlyAbove1LineEdit, \
                 ), \
                (self.ui.detectSpikes1But, \
                ) \
            ), \
        )
        
        self.spikeSavefilesFish2Unlocker = ( \
            ( \
                (self.ui.saveSpikes2LineEdit, \
                 self.ui.saveWindowLengths2LineEdit, \
                 self.ui.onlyAbove2LineEdit, \
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
                (self.ui.defaultSVMValuesBut, \
                 self.ui.cStartLineEdit, \
                 self.ui.cStepLineEdit, \
                 self.ui.cStopLineEdit, \
                 self.ui.cValueLineEdit, \
                 self.ui.gStartLineEdit, \
                 self.ui.gStepLineEdit, \
                 self.ui.gStopLineEdit, \
                 self.ui.gValueLineEdit, \
                 self.ui.optimizeSVMBut, \
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
        
        # Connects each field to its unlocker (dependencies and unlockers)
        self.Fields = {self.ui.loadTS1LineEdit: self.loadTSFish1Unlocker, \
                       
                       self.ui.loadTS2LineEdit: self.loadTSFish2Unlocker, \
                       
                       self.ui.lowSaturation1LineEdit: self.spikeParametersFish1Unlocker, \
                       self.ui.highSaturation1LineEdit: self.spikeParametersFish1Unlocker, \
                       self.ui.taps1LineEdit: self.spikeParametersFish1Unlocker, \
                       self.ui.cutoff1LineEdit: self.spikeParametersFish1Unlocker, \
                       self.ui.thresholdLevel1LineEdit: self.spikeParametersFish1Unlocker, \
                       self.ui.minlevel1LineEdit: self.spikeParametersFish1Unlocker, \
                       
                       self.ui.lowSaturation2LineEdit: self.spikeParametersFish2Unlocker, \
                       self.ui.highSaturation2LineEdit: self.spikeParametersFish2Unlocker, \
                       self.ui.taps2LineEdit: self.spikeParametersFish2Unlocker, \
                       self.ui.cutoff2LineEdit: self.spikeParametersFish2Unlocker, \
                       self.ui.thresholdLevel2LineEdit: self.spikeParametersFish2Unlocker, \
                       self.ui.minlevel2LineEdit: self.spikeParametersFish2Unlocker, \
                       
                       self.ui.saveSpikes1LineEdit: self.spikeSavefilesFish1Unlocker, \
                       self.ui.saveWindowLengths1LineEdit: self.spikeSavefilesFish1Unlocker, \
                       self.ui.onlyAbove1LineEdit: self.spikeSavefilesFish1Unlocker, \
                       
                       self.ui.saveSpikes2LineEdit: self.spikeSavefilesFish2Unlocker, \
                       self.ui.saveWindowLengths2LineEdit: self.spikeSavefilesFish2Unlocker, \
                       self.ui.onlyAbove2LineEdit: self.spikeSavefilesFish2Unlocker, \
                       
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
    
    def connectFileFields(self):
        
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
        # Manually locks testing line fields
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
