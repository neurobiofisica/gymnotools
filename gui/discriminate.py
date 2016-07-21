import os, sys, inspect

import numpy as np

from PyQt4 import QtCore, QtGui
from discriminate_interface import Ui_discriminateWindow

sys.path.append( os.path.realpath('../') )
from python.plotIPIandSVM import plotIPIandSVM

class DiscriminateWindow(QtGui.QDialog):
    def __init__(self, app, parent=None):
        self.app = app
        
        QtGui.QWidget.__init__(self)
        self.setFocusPolicy( QtCore.Qt.StrongFocus )
        self.setFocus()
        
        self.showMaximized()
        
        self.ui = Ui_discriminateWindow()
        self.ui.setupUi(self)

        self.defaultValues = {self.ui.lowSaturationLineEdit: -9.9, \
                              self.ui.highSaturationLineEdit: 9.9, \

                              self.ui.tapsLineEdit: 301, \

                              self.ui.cutoffLineEdit: 1.0, \

                              self.ui.thresholdLevelLineEdit: 1.0, \

                              self.ui.loadChirpsModelLineEdit: os.path.dirname(os.path.realpath(__file__)) + '/../chirpDetector/chirpModel_abs.chirpmodel'
                             }

        for field in self.defaultValues.keys():
            field.setText(str(self.defaultValues[field]))
        
        # LineFields List -> for saving parameters
        self.lineFieldsList = (self.ui.loadTimeseriesLineEdit, \
                               self.ui.loadChirpsModelLineEdit, \
                               self.ui.saveChirpsLineEdit, \
                               self.ui.loadChirpsLineEdit, \
                               self.ui.lowSaturationLineEdit, \
                               self.ui.highSaturationLineEdit, \
                               self.ui.tapsLineEdit, \
                               self.ui.cutoffLineEdit, \
                               self.ui.thresholdLevelLineEdit, \
                               self.ui.saveSpikesLineEdit, \
                               self.ui.loadSpikesLineEdit, \
                               self.ui.loadWinlen1LineEdit, \
                               self.ui.loadWinlen2LineEdit, \
                               self.ui.loadFilterLineEdit, \
                               self.ui.loadRescaleLineEdit, \
                               self.ui.loadSVMModelLineEdit, \
                               self.ui.saveSinglefishLineEdit, \
                               self.ui.saveProbLineEdit, \
                               self.ui.minWinLineEdit, \
                               self.ui.onlyAboveLineEdit, \
                               self.ui.loadSinglefishLineEdit, \
                               self.ui.loadProbLineEdit, \
                               self.ui.saveDBLineEdit, \
                               self.ui.loadDBLineEdit, \
                               self.ui.saveTimestampsLineEdit, \
                               self.ui.loadTimestampsLineEdit, \
                               )
        
        # Program objects -> they must be parameters for the GarbageCollector
        # do not clean them
        self.detectChirpsProgram = QtCore.QProcess()
        self.filterAssistProgram = QtCore.QProcess()
        self.thresholdAssistProgram = QtCore.QProcess()
        self.minlevelAssistProgram = QtCore.QProcess()
        self.verifySpikesProgram = QtCore.QProcess()
        self.detectSpikesProgram = QtCore.QProcess()
        self.applySVMProgram = QtCore.QProcess()
        self.applyContinuityProgram = QtCore.QProcess()
        self.detectTimestampsProgram = QtCore.QProcess()
        
        self.dicProgram = {'detectaChirp': (self.detectChirpsProgram, ), \
                           'winview': (self.verifySpikesProgram, ), \
                           'spikes': (self.detectSpikesProgram, ), \
                           'singlefish': (self.applySVMProgram, ), \
                           'recog': (self.applyContinuityProgram, ), \
                           'detectIPI': (self.detectTimestampsProgram, ), \
                           }
        
        self.cancelled = False
        
        self.ParametersLayout = (self.ui.step1ParametersLayout, \
                            self.ui.step2ParametersLayout, \
                            self.ui.step3ParametersLayout, \
                            self.ui.step4ParametersLayout, \
                            self.ui.step5ParametersLayout, \
                            )
        
        self.titleLabels = (self.ui.step1TitleLabel, \
                            self.ui.step2TitleLabel, \
                            self.ui.step3TitleLabel, \
                            self.ui.step4TitleLabel, \
                            self.ui.step5TitleLabel
                            )
        
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
        
        self.defineFieldsType()
        self.connectFileFields()
        self.connectUnlockFields()
        self.connectButtons()
        
        self.initialClickState()
        
        # Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
    
    def connectButtons(self):
        QtCore.QObject.connect(self.ui.detectChirpsBut, QtCore.SIGNAL('clicked()'), self.detectChirps)

        QtCore.QObject.connect(self.ui.saveParametersBut, QtCore.SIGNAL('clicked()'), self.saveParameters)
        QtCore.QObject.connect(self.ui.loadParametersBut, QtCore.SIGNAL('clicked()'), self.loadParameters)
        
        QtCore.QObject.connect(self.ui.detectSpikesBut, QtCore.SIGNAL('clicked()'), self.detectSpikes)
        QtCore.QObject.connect(self.ui.verifySpikesBut, QtCore.SIGNAL('clicked()'), self.verifySpikes)
        
        QtCore.QObject.connect(self.ui.applySVMBut, QtCore.SIGNAL('clicked()'), self.applySVM)
        
        QtCore.QObject.connect(self.ui.applyContinuityBut, QtCore.SIGNAL('clicked()'), self.applyContinuity)
        
        QtCore.QObject.connect(self.ui.detectTimestampsBut, QtCore.SIGNAL('clicked()'), self.detectTimestamps)
        
        QtCore.QObject.connect(self.ui.verifyCorrectTimestampsBut, QtCore.SIGNAL('clicked()'), self.verifyAndCorrect)

    def detectChirps(self):
        print 'detectaChirp'

        TSName = self.ui.loadTimeseriesLineEdit.text()
        chirpsModel = self.ui.loadChirpsModelLineEdit.text()
        saveChirps = self.ui.saveChirpsLineEdit.text()
        lowSat = self.ui.lowSaturationLineEdit.text()
        highSat = self.ui.highSaturationLineEdit.text()

        dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        # Same name of self.dicProgram
        self.programname = 'detectaChirp'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.detectChirpsProgram.start('./../chirpDetector/detectaChirp', \
                                        ['--saturation=%s,%s'%(lowSat,highSat), \
                                        TSName, \
                                        chirpsModel, \
                                        saveChirps, \
                                        ])

        self.cancelled = False
        def detectChirpsFinish(ret, exitStatus):
            self.app.restoreOverrideCursor()
            dialog.hide()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.ui.loadChirpsLineEdit.setText(saveChirps)
            else:
                return None

        QtCore.QObject.connect(self.detectChirpsProgram, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), detectChirpsFinish)
        QtCore.QObject.connect(self.detectChirpsProgram, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.detectChirpsProgram, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)


    
    def detectSpikes(self):
        print 'spikes'
        TSName = self.ui.loadTimeseriesLineEdit.text()
        chirpsFile = None #########################################
        hilbName = self.ui.saveLoadHilbLineEdit.text()
        taps = self.ui.tapsLineEdit.text()
        cutoff = self.ui.cutoffLineEdit.text()
        threshold = self.ui.thresholdLevelLineEdit.text()
        refractory = self.ui.refractoryLineEdit.text()
        maxSize = self.ui.maxSizeLineEdit.text()
        saveSpikes = self.ui.saveSpikesLineEdit.text()
        useHilb = self.ui.useHilb1CheckBox.isChecked()

        listArgs = ['--chirps_file=%s'%chirpsFile, \
                            '--detection=%s'%(threshold), \
                            '--refractory=%s'%(refractory), \
                            '--max_size=%s'%(maxSize), \
                            '--detection=%s'%threshold, \
                            TSName, \
                            hilbName, \
                            saveSpikes]
        if useHilb == True:
            listArgs.insert(0, '--useHilbert')
        else:
            listArgs.insert(3, '--numtaps=%s'%taps)
            listArgs.insert(4, '--cutoff=%s'%cutoff)

        print(repr(useHilb))
        print(listArgs)
        
        dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        # Same name of self.dicProgram
        self.programname = 'spikes'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.detectSpikesProgram.start('./../spikes/spikes', \
                                        listArgs)
        
        self.cancelled = False
        def detectSpikesFinish(ret, exitStatus):
            self.app.restoreOverrideCursor()
            dialog.hide()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.ui.loadSpikesLineEdit.setText(saveSpikes)
            else:
                return None
        
        QtCore.QObject.connect(self.detectSpikesProgram, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), detectSpikesFinish)
        QtCore.QObject.connect(self.detectSpikesProgram, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.detectSpikesProgram, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
    
    def verifySpikes(self):
        print 'winview'
        spikesName = self.ui.loadSpikesLineEdit.text()
        TSName = self.ui.loadTimeseriesLineEdit.text()
        
        # Same name of self.dicProgram
        self.programname = 'winview'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        if TSName != '':
            self.verifySpikesProgram.start('./../winview/winview', [spikesName, TSName])
        else:
            self.verifySpikesProgram.start('./../winview/winview', [spikesName])
        
        self.cancelled = False
        def verifySpikesFinish(ret, exitStatus):
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                pass
            else:
                print 'stdout:\n' + self.verifySpikesProgram.readAllStandardOutput()
                print 'stderr:\n' + self.verifySpikesProgram.readAllStandardError()
                return None
        
        QtCore.QObject.connect(self.verifySpikesProgram, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), verifySpikesFinish)
    
    def applySVM(self):
        print 'singlefish'
        minWin = self.ui.minWinLineEdit.text()
        onlyAbove = self.ui.onlyAboveLineEdit.text()
        winLen1 = self.ui.loadWinlen1LineEdit.text()
        winLen2 = self.ui.loadWinlen2LineEdit.text()
        lowSaturation = self.ui.lowSaturationLineEdit.text()
        highSaturation = self.ui.highSaturationLineEdit.text()
        TSName = self.ui.loadTimeseriesLineEdit.text()
        spikesName = self.ui.loadSpikesLineEdit.text()
        scaleName = self.ui.loadRescaleLineEdit.text()
        filterName = self.ui.loadFilterLineEdit.text()
        svmName = self.ui.loadSVMModelLineEdit.text()
        saveSinglefish = self.ui.saveSinglefishLineEdit.text()
        saveProb = self.ui.saveProbLineEdit.text()
        
        winlen = max( (self.mean_stdWinLen(winLen1), self.mean_stdWinLen(winLen2)) )
        
        dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        # Same name of self.dicProgram
        self.programname = 'singlefish'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )

        ################# maxsize = %d,%winlen, \
        self.applySVMProgram.start('./../singlefish/singlefish', \
                                    ['--minwins=%s'%minWin, \
                                    '--onlyabove=%s'%onlyAbove, \
                                    '--saturation=%s,%s'%(lowSaturation,highSaturation), \
                                    '--minprob=0.80', \
                                    TSName, \
                                    spikesName, \
                                    scaleName, \
                                    filterName, \
                                    svmName, \
                                    saveSinglefish, \
                                    saveProb])
        
        self.cancelled = False
        def applySVMFinish(ret, exitStatus):
            print 'singlefish finished (%d,%s)'%(ret, repr(exitStatus))
            self.app.restoreOverrideCursor()
            dialog.hide()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.ui.loadSinglefishLineEdit.setText(saveSinglefish)
                self.ui.loadProbLineEdit.setText(saveProb)
            else:
                print 'stdout:\n' + self.applySVMProgram.readAllStandardOutput()
                print 'stderr:\n' + self.applySVMProgram.readAllStandardError()
                return None
        
        QtCore.QObject.connect(self.applySVMProgram, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), applySVMFinish)
        QtCore.QObject.connect(self.applySVMProgram, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.applySVMProgram, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
    
    def applyContinuity(self):
        print 'recog'
        self.lowSaturation = self.ui.lowSaturationLineEdit.text()
        self.highSaturation = self.ui.highSaturationLineEdit.text()
        self.TSName = self.ui.loadTimeseriesLineEdit.text()
        self.spikesName = self.ui.loadSpikesLineEdit.text()
        self.singlefishName = self.ui.loadSinglefishLineEdit.text()
        self.probName = self.ui.loadProbLineEdit.text()
        self.saveDBName = self.ui.saveDBLineEdit.text()
        self.TSoutput = self.saveDBName.split('.')[0] + '.timestamps'
       
        if os.path.isfile(self.saveDBName):
            dialog = QtGui.QMessageBox()
            dialog.setModal(True)
            dialog.setWindowTitle('Warning')
            dialog.setText('You want to override the original DB or apply over it?\n' + \
                           '(when applying over it, it will only substitute the spikes that' + \
                           'had euclidean distance inferior to the stored on the DB)')
            dialog.addButton(QtGui.QPushButton('Override'), QtGui.QMessageBox.YesRole) #0
            dialog.addButton(QtGui.QPushButton('Apply over'), QtGui.QMessageBox.NoRole) #1
            dialog.addButton(QtGui.QMessageBox.Cancel)
            
            ret = dialog.exec_()
            
            if ret == QtGui.QMessageBox.Cancel:
                return None
            elif ret == 0: #Override
                print 'Removing DB file...'
                os.remove(self.saveDBName)
            else: #ret == 1 -> Apply over
                pass
        
        self.recogPassed = False
        self.recog(1)
    
    def recog(self, d):
        # TODO: saturation level??
        print 'direction = %d'%d
        
        self.dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
    
        self.programname = 'recog'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.applyContinuityProgram.start('./../recog/recog', \
                                          ['iterate', \
                                           '--saturation=%s,%s'%(self.lowSaturation, self.highSaturation), \
                                           '--direction=%d'%d, \
                                           self.saveDBName, \
                                           self.spikesName, \
                                           self.singlefishName, \
                                           self.probName, \
                                           self.TSoutput])
        
        self.cancelled = False
        def recogFinish(ret, exitStatus):
            print 'recog finished (%d,%s)'%(ret, repr(exitStatus))
            self.dialog.hide()
            self.app.restoreOverrideCursor()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                if (self.recogPassed == False):
                    self.recogPassed = True
                    if d == 1:
                        self.recog(-1)
                    else:
                        self.recog(1)
                else:
                    self.ui.loadDBLineEdit.setText(self.saveDBName)
            else:
                print 'stdout:\n' + self.applyContinuityProgram.readAllStandardOutput()
                print 'stderr:\n' + self.applyContinuityProgram.readAllStandardError()
                return None
        
        
        QtCore.QObject.connect(self.applyContinuityProgram, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), recogFinish)
        QtCore.QObject.connect(self.applyContinuityProgram, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.applyContinuityProgram, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
        
    
    def mean_stdWinLen(self, winlenFilename):
        data = np.loadtxt(str(winlenFilename))
        m = np.mean(data)
        s = np.std(data)
        return int(np.ceil(m+s))
    
    def detectTimestamps(self):
        print 'detectIPI'
        DBName = self.ui.loadDBLineEdit.text()
        saveTimestamps = self.ui.saveTimestampsLineEdit.text()
        
        dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        self.programname = 'detectIPI'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.detectTimestampsProgram.start('python', \
                                           ['./../detectIPI/detectIPI.py', \
                                            DBName, \
                                            saveTimestamps])
        
        self.cancelled = False
        def detectTimestampsFinish(ret, exitStatus):
            print 'detectIPI finished (%d,%s)'%(ret, repr(exitStatus))
            dialog.hide()
            self.app.restoreOverrideCursor()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.ui.loadTimestampsLineEdit.setText(saveTimestamps)
            else:
                print 'stdout:\n' + self.detectSpikesProgram.readAllStandardOutput()
                print 'stderr:\n' + self.detectSpikesProgram.readAllStandardError()
                return None
        
        QtCore.QObject.connect(self.detectTimestampsProgram, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), detectTimestampsFinish)
        QtCore.QObject.connect(self.detectTimestampsProgram, QtCore.SIGNAL('readyReadStandardOutput()'), self.printAllStandardOutput)
        QtCore.QObject.connect(self.detectTimestampsProgram, QtCore.SIGNAL('readyReadStandardError()'), self.printAllStandardError)
    
    def verifyAndCorrect(self):
        print 'plotIPIandSVM'
        lowSaturation = float(self.ui.lowSaturationLineEdit.text())
        highSaturation = float(self.ui.highSaturationLineEdit.text())
        DBName = str(self.ui.loadDBLineEdit.text())
        timeseriesFile = open(self.ui.loadTimeseriesLineEdit.text(),'r')
        spikesFile = open(self.ui.loadSpikesLineEdit.text(), 'r')
        timestampsFile = str(self.ui.loadTimestampsLineEdit.text())
        
        self.programname = 'plotIPIandSVM'
        
        timeseriesName = str(timeseriesFile.name.split('/')[-1].split('.')[0])
        if os.path.isdir(timeseriesName) == False:
            os.makedirs(str(timeseriesName))
        dbname = str(DBName.split('/')[-1].split('.')[0] + '_undo.keys')
        undoFilename = str(timeseriesName + '/' + dbname)
        open(undoFilename,'a').close()
        
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        plotVerify = plotIPIandSVM.PlotData(self.app, DBName, spikesFile, timeseriesFile, undoFilename, timeseriesName, (lowSaturation, highSaturation), 120., 90.)
        pickVerify = plotIPIandSVM.PickPoints(plotVerify, timestampsFile)
        self.app.restoreOverrideCursor()
        
        plotVerify.show()
        
    def printAllStandardOutput(self):
        print '%s\n'%self.programname
        for program in self.dicProgram[self.programname]:
            print program.readAllStandardOutput()
    
    def printAllStandardError(self):
        print '%s\n'%self.programname
        for program in self.dicProgram[self.programname]:
            print program.readAllStandardError()
    
    def raiseLongTimeInformation(self):
        dialog = QtGui.QMessageBox()
        dialog.setWindowTitle('Information')
        dialog.setText("This may take a while...\nTime for a coffee!\n")
        dialog.setModal(True)
        self.CancelBut = dialog.addButton(QtGui.QMessageBox.Cancel)
        QtCore.QObject.connect(self.CancelBut, QtCore.SIGNAL('clicked()'), self.cancelApp)
        dialog.show()
        return dialog
    
    def cancelApp(self):
        print 'Cancelled.'
        self.cancelled = True
        self.app.restoreOverrideCursor()
        for l in self.dicProgram.values():
            for program in l:
                program.close()
    
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
    
    def raiseParameterError(self, text):
        QtGui.QMessageBox.critical(self, "ERROR", text + "Please check your parameters.", QtGui.QMessageBox.Ok )
    
    def saveParameters(self):
        saveFilename = QtGui.QFileDialog.getSaveFileName(self, 'Save Parameters File', '', 'Parameters File (*.discparameters) (*.discparameters);;All files (*.*) (*.*)')
        saveFile = open(saveFilename, 'w')
        for element in self.lineFieldsList:
            if isinstance(element, QtGui.QLineEdit):
                saveFile.write( '%s\t%s\n'%(element.objectName(), element.text()) )
        saveFile.close()

    def loadParameters(self):
        loadFilename = QtGui.QFileDialog.getOpenFileName(self, 'Load Parameters File', '', 'Parameters File (*.discparameters) (*.discparameters);;All files (*.*) (*.*)')
        loadFile = open(loadFilename, 'r')
        for line in loadFile.xreadlines():
            objectName, Value = line.split('\t')
            Value = Value.strip()
            if Value != '':
                for element in self.lineFieldsList:
                    if element.objectName() == objectName:
                        element.setText(Value)
                        break
    
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
    
    def defineFieldsType(self):
        self.fieldsType = {self.ui.loadTimeseriesLineEdit: 'load', \
                           self.ui.loadChirpsModelLineEdit: 'load', \
                           self.ui.saveChirpsLineEdit: 'save', \
                           self.ui.loadChirpsLineEdit: 'load', \

                           self.ui.saveLoadHilbLineEdit: 'save', \
                           self.ui.useHilbCheckBox: 'not-check', \
                           
                           self.ui.lowSaturationLineEdit: 'float', \
                           self.ui.highSaturationLineEdit: 'float', \
                           self.ui.tapsLineEdit: 'int', \
                           self.ui.cutoffLineEdit: 'float', \
                           self.ui.thresholdLevelLineEdit: 'float', \
                           
                           self.ui.saveSpikesLineEdit: 'save', \
                           
                           self.ui.loadSpikesLineEdit: 'load', \
                           self.ui.loadWinlen1LineEdit: 'load', \
                           self.ui.loadWinlen2LineEdit: 'load', \
                           self.ui.loadFilterLineEdit: 'load', \
                           self.ui.loadRescaleLineEdit: 'load', \
                           self.ui.loadSVMModelLineEdit: 'load', \
                           
                           self.ui.saveSinglefishLineEdit: 'save', \
                           self.ui.saveProbLineEdit: 'save', \
                           self.ui.minWinLineEdit: 'int', \
                           self.ui.onlyAboveLineEdit: 'float', \
                           
                           self.ui.loadSinglefishLineEdit: 'load', \
                           self.ui.loadProbLineEdit: 'load', \
                           
                           self.ui.saveDBLineEdit: 'save', \
                           
                           self.ui.loadDBLineEdit: 'load', \
                           
                           self.ui.saveTimestampsLineEdit: 'save', \
                           
                           self.ui.loadTimestampsLineEdit: 'load', \
                           }
        
        for field in self.fieldsType.keys():
            if self.fieldsType[field] == 'int':
                field.setValidator( QtGui.QIntValidator() )
            elif self.fieldsType[field] == 'float':
                field.setValidator( QtGui.QDoubleValidator() )
        
        self.fileFieldsExtension = {
            self.ui.loadTimeseriesLineEdit: 'Timeseries on format I32 file (*.*) (*.*)', \
            self.ui.loadChirpsModelLineEdit: 'Chirp model file (*.chirpmodel) (*.chirpmodel)', \
            self.ui.saveChirpsLineEdit: 'Chirps location file (*.chirps) (*.chirps)', \
            self.ui.loadChirpsLineEdit: 'Chirps location file (*.chirps), (*.chirps)', \
            self.ui.saveLoadHilbLineEdit: 'Hilbert transform (*.hilb) (*.hilb)', \
            self.ui.saveSpikesLineEdit: 'Spikes File (*.spikes) (*.spikes)', \
            self.ui.loadSpikesLineEdit: 'Spikes File (*.spikes) (*.spikes)', \
            self.ui.loadWinlen1LineEdit: 'Window Length File (*.winlen) (*.winlen)', \
            self.ui.loadWinlen2LineEdit: 'Window Length File (*.winlen) (*.winlen)', \
            self.ui.loadFilterLineEdit: 'Filter File (*.filter) (*.filter)', \
            self.ui.loadRescaleLineEdit: 'Rescale File (*.scale) (*.scale)', \
            self.ui.loadSVMModelLineEdit: 'SVM Model File (*.svmmodel) (*.svmmodel)', \
            self.ui.saveSinglefishLineEdit: 'Only SVM discriminated Singlefish File (*.singlefish) (*.singlefish)', \
            self.ui.saveProbLineEdit: 'All SVM Probabilities File (*.prob) (*.prob)', \
            self.ui.loadSinglefishLineEdit: 'Only SVM discriminated Singlefish File (*.singlefish) (*.singlefish)', \
            self.ui.loadProbLineEdit: 'All SVM Probabilities File (*.prob) (*.prob)', \
            self.ui.saveDBLineEdit: 'Discriminated spikes DataBase (*.db) (*.db)', \
            self.ui.loadDBLineEdit: 'Discriminated spikes DataBase (*.db) (*.db)', \
            self.ui.saveTimestampsLineEdit: 'Completely discriminated timestamps File (*.timestamps) (*.timestamps)', \
            self.ui.loadTimestampsLineEdit: 'Completely discriminated timestamps File (*.timestamps) (*.timestamps)', \
            }
    
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
    
    def connectFileFields(self):
        FileFields = (self.ui.loadTimeseriesLineEdit, \
                      self.ui.loadChirpsModelLineEdit, \
                      self.ui.saveChirpsLineEdit, \
                      self.ui.loadChirpsLineEdit, \
                      self.ui.saveLoadHilbLineEdit, \
                      self.ui.saveSpikesLineEdit, \
                      self.ui.loadSpikesLineEdit, \
                      self.ui.loadWinlen1LineEdit, \
                      self.ui.loadWinlen2LineEdit, \
                      self.ui.loadFilterLineEdit, \
                      self.ui.loadRescaleLineEdit, \
                      self.ui.loadSVMModelLineEdit, \
                      self.ui.saveSinglefishLineEdit, \
                      self.ui.saveProbLineEdit, \
                      self.ui.loadSinglefishLineEdit, \
                      self.ui.loadProbLineEdit, \
                      self.ui.saveDBLineEdit, \
                      self.ui.loadDBLineEdit, \
                      self.ui.saveTimestampsLineEdit, \
                      self.ui.loadTimestampsLineEdit, \
                      )
        
        for field in FileFields:
            QtCore.QObject.connect(field, QtCore.SIGNAL('clicked()'), self.fileFieldHandler)
    
    def connectUnlockFields(self):
        
        # The first element of the unlockers is the list of fields that block others
        # The second element are the fields that are release by that edition
        self.loadTimeseriesUnlocker = ( \
            ( \
                (self.ui.loadTimeseriesLineEdit, \
                ), \
                (self.ui.saveChirpsLineEdit, \
                 self.ui.lowSaturationLineEdit, \
                 self.ui.highSaturationLineEdit, \
                ) \
            ), \
        )

        self.loadChirpsModelUnlocker = ( \
            ( \
                (self.ui.loadChirpsModelLineEdit, \
                 self.ui.saveChirpsLineEdit, \
                ), \
                (self.ui.detectChirpsBut, \
                )
            ), \
        )

        self.loadChirpsUnlocker = ( \
            ( \
                (self.ui.loadChirpsLineEdit, \
                ), \
                (self.ui.saveLoadHilbLineEdit, \
                 self.ui.tapsLineEdit, \
                 self.ui.cutoffLineEdit, \
                ) \
            ), \
        )


        self.clickUseHilb = ( \
            ( \
                (self.ui.useHilbCheckBox, \
                ), \
                (self.ui.tapsLineEdit, \
                 self.ui.cutoffLineEdit, \
                ) \
            ), \
        )
        
        self.spikeParametersUnlocker = ( \
            ( \
                (self.ui.loadTimeseriesLineEdit, \
                 self.ui.lowSaturationLineEdit, \
                 self.ui.highSaturationLineEdit, \
                 self.ui.tapsLineEdit, \
                 self.ui.cutoffLineEdit, \
                 self.ui.thresholdLevelLineEdit, \
                ), \
                (self.ui.saveSpikesLineEdit, \
                ) \
            ), \
            #( \
            #    (self.ui.tapsLineEdit, \
            #     self.ui.cutoffLineEdit, \
            #    ), \
            #    (self.ui.thresholdLevelLineEdit, \
            #    )
            #), \
        )
        
        self.spikeSavefileUnlocker = ( \
            ( \
                (self.ui.loadTimeseriesLineEdit, \
                 self.ui.lowSaturationLineEdit, \
                 self.ui.highSaturationLineEdit, \
                 self.ui.saveSpikesLineEdit, \
                ), \
                (self.ui.detectSpikesBut, \
                ) \
            ), \
        )
        
        self.SVMLoadParametersUnlocker = ( \
            ( \
                (self.ui.loadSpikesLineEdit, \
                ), \
                (self.ui.verifySpikesBut, \
                ) \
            ), \
            ( \
                (self.ui.loadTimeseriesLineEdit, \
                 self.ui.loadSpikesLineEdit, \
                 self.ui.loadWinlen1LineEdit, \
                 self.ui.loadWinlen2LineEdit, \
                 self.ui.loadFilterLineEdit, \
                 self.ui.loadRescaleLineEdit, \
                 self.ui.loadSVMModelLineEdit, \
                ), \
                (self.ui.saveSinglefishLineEdit, \
                 self.ui.saveProbLineEdit, \
                 self.ui.minWinLineEdit, \
                 self.ui.onlyAboveLineEdit, \
                )
            ), \
        )
        
        self.SVMSaveParametersUnlocker = ( \
            ( \
                (self.ui.loadTimeseriesLineEdit, \
                 self.ui.lowSaturationLineEdit, \
                 self.ui.highSaturationLineEdit, \
                 self.ui.saveSinglefishLineEdit, \
                 self.ui.saveProbLineEdit, \
                 self.ui.minWinLineEdit, \
                 self.ui.onlyAboveLineEdit, \
                ), \
                (self.ui.applySVMBut, \
                )
            ), \
        )
        
        self.loadContinuityParametersUnlocker = ( \
            ( \
                (self.ui.loadSinglefishLineEdit, \
                 self.ui.loadProbLineEdit, \
                ), \
                (self.ui.saveDBLineEdit, \
                )
            ), \
        )
        
        self.saveDBUnlocker = ( \
            ( \
                (self.ui.loadTimeseriesLineEdit, \
                 self.ui.lowSaturationLineEdit, \
                 self.ui.highSaturationLineEdit, \
                 self.ui.saveDBLineEdit, \
                ), \
                (self.ui.applyContinuityBut, \
                )
            ), \
        )
        
        self.loadDBUnlocker = ( \
            ( \
                (self.ui.loadDBLineEdit, \
                ), \
                (self.ui.saveTimestampsLineEdit, \
                )
            ), \
        )
        
        self.saveTimestampsUnlocker = ( \
            ( \
                (self.ui.loadTimeseriesLineEdit, \
                 self.ui.saveTimestampsLineEdit, \
                ), \
                (self.ui.detectTimestampsBut, \
                )
            ), \
        )
        
        self.loadTimestampsUnlocker = ( \
            ( \
                (self.ui.loadTimeseriesLineEdit, \
                 self.ui.loadTimestampsLineEdit, \
                ), \
                (self.ui.verifyCorrectTimestampsBut, \
                )
            ), \
        )
        
        # Connects each field to its unlocker (dependencies and unlockers)
        self.Fields = {self.ui.loadTimeseriesLineEdit: self.loadTimeseriesUnlocker, \
                       self.ui.loadChirpsModelLineEdit: self.loadChirpsModelUnlocker, \
                       self.ui.saveChirpsLineEdit: self.loadChirpsModelUnlocker, \
                       self.ui.loadChirpsLineEdit: self.loadChirpsUnlocker, \
                       self.ui.useHilbCheckBox: self.clickUseHilb, \
                       self.ui.saveLoadHilbLineEdit: self.spikeParametersUnlocker, \
                       self.ui.lowSaturationLineEdit: self.spikeParametersUnlocker, \
                       self.ui.highSaturationLineEdit: self.spikeParametersUnlocker, \
                       self.ui.tapsLineEdit: self.spikeParametersUnlocker, \
                       self.ui.cutoffLineEdit: self.spikeParametersUnlocker, \
                       self.ui.thresholdLevelLineEdit: self.spikeParametersUnlocker, \
                       self.ui.saveSpikesLineEdit: self.spikeSavefileUnlocker, \
                       self.ui.loadSpikesLineEdit: self.SVMLoadParametersUnlocker, \
                       self.ui.loadWinlen1LineEdit: self.SVMLoadParametersUnlocker, \
                       self.ui.loadWinlen2LineEdit: self.SVMLoadParametersUnlocker, \
                       self.ui.loadFilterLineEdit: self.SVMLoadParametersUnlocker, \
                       self.ui.loadRescaleLineEdit: self.SVMLoadParametersUnlocker, \
                       self.ui.loadSVMModelLineEdit: self.SVMLoadParametersUnlocker, \
                       self.ui.saveSinglefishLineEdit: self.SVMSaveParametersUnlocker, \
                       self.ui.saveProbLineEdit: self.SVMSaveParametersUnlocker, \
                       self.ui.minWinLineEdit: self.SVMSaveParametersUnlocker, \
                       self.ui.onlyAboveLineEdit: self.SVMSaveParametersUnlocker, \
                       self.ui.loadSinglefishLineEdit: self.loadContinuityParametersUnlocker, \
                       self.ui.loadProbLineEdit: self.loadContinuityParametersUnlocker, \
                       self.ui.saveDBLineEdit: self.saveDBUnlocker, \
                       self.ui.loadDBLineEdit: self.loadDBUnlocker, \
                       self.ui.saveTimestampsLineEdit: self.saveTimestampsUnlocker, \
                       self.ui.loadTimestampsLineEdit: self.loadTimestampsUnlocker, \
                       }
        
        for field in self.Fields.keys():
            if isinstance(field, QtGui.QLineEdit):
                QtCore.QObject.connect(field, QtCore.SIGNAL('textChanged(QString)'), self.tryUnlock)
            elif isinstance(field, QtGui.QCheckBox):
                QtCore.QObject.connect(field, QtCore.SIGNAL('stateChanged(int)'), self.tryUnlock)
    
    def initialClickState(self):
        for tup in self.Fields.values():
            for locker,locked in tup:
                self.switchLockState(locked, False)
    
    def tryUnlock(self, text):
        field = self.sender()
        
        for tup in self.Fields[field]:
            allChecked = True
            for f in tup[0]:
                allChecked = allChecked and self.verifyField(f)
        
            self.switchLockState(tup[1], allChecked)
    
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
        elif self.fieldsType[field] == 'not-check':
            return not(field.isChecked())

        else:
            if data != '':
                return True
            else:
                return False
    
    def switchLockState(self, lockerList, state):
        for el in lockerList:
            el.setEnabled(state)
            if el in self.defaultValues.keys():
                if state == False:
                    el.setText( str(self.defaultValues[el]) )

if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)
    
    myapp = DiscriminateWindow(app)
    
    myapp.show()
    sys.exit(app.exec_())
