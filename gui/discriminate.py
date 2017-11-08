import os, sys, inspect

import recogdb

import numpy as np

from PyQt5 import QtCore, QtWidgets, QtGui
try:
    from PyQt5.QtCore import QString
except:
    QString = str
from gui.discriminate_interface import Ui_discriminateWindow

sys.path.append( os.path.realpath('../') )
#from python.plotIPIandSVM import plotIPIandSVM

class DiscriminateWindow(QtWidgets.QDialog):
    def __init__(self, app, parent=None):
        self.app = app
        
        QtWidgets.QWidget.__init__(self)
        self.setFocusPolicy( QtCore.Qt.StrongFocus )
        self.setFocus()
        
        self.showMaximized()
        
        self.ui = Ui_discriminateWindow()
        self.ui.setupUi(self)

        # LineFields List -> for saving parameters
        self.lineFieldsList = (self.ui.loadTimeseriesLineEdit, \
                               self.ui.saveHilbLineEdit, \
                               self.ui.loadHilbLineEdit, \
                               self.ui.lowSaturationLineEdit, \
                               self.ui.highSaturationLineEdit, \
                               self.ui.gmeanLineEdit, \
                               self.ui.tapsLineEdit, \
                               self.ui.lowCutoffLineEdit, \
                               self.ui.highCutoffLineEdit, \
                               self.ui.subsampLineEdit, \
                               self.ui.minWaveletLineEdit, \
                               self.ui.maxWaveletLineEdit, \
                               self.ui.stepWaveletLineEdit, \
                               self.ui.peakLineEdit, \
                               self.ui.minHilbLineEdit, \
                               self.ui.toleranceLineEdit, \
                               self.ui.saveSpikesLineEdit, \
                               self.ui.loadSpikesLineEdit, \
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
        self.calcHilbProgram = QtCore.QProcess()
        self.verifySpikesProgram = QtCore.QProcess()
        self.detectSpikesProgram = QtCore.QProcess()
        self.applySVMProgram = QtCore.QProcess()
        self.applyContinuityProgram = QtCore.QProcess()
        self.detectTimestampsProgram = QtCore.QProcess()
        self.plotIPIandSVMProgram = QtCore.QProcess()
        
        self.dicProgram = {'calcHilb': (self.calcHilbProgram, ), \
                           'winview': (self.verifySpikesProgram, ), \
                           'spikes': (self.detectSpikesProgram, ), \
                           'singlefish': (self.applySVMProgram, ), \
                           'recog': (self.applyContinuityProgram, ), \
                           'detectIPI': (self.detectTimestampsProgram, ), \
                           'plotIPIandSVM': (self.plotIPIandSVMProgram, ), \
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
            if isinstance(layout, QtWidgets.QLayout):
                for i in xrange(layout.count()):
                    try:
                        layout.itemAt(i).widget().hide()
                    except:
                        pass
            elif isinstance(layout, QtWidgets.QWidget):
                layout.hide()'''
        
        for label in self.titleLabels:
            label.clicked.connect(self.expandLayout)
        
        self.defineFieldsType()
        self.connectFileFields()
        self.connectUnlockFields()
        self.connectButtons()
        
        self.initialClickState()
        
        # Unlock fields based on default values
        for field,unlock in self.Fields.items():
            self.tryUnlockRaw(field)

        # Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
    
    def connectButtons(self):
        self.ui.calcHilbBut.clicked.connect(self.calcHilb)
        self.ui.saveParametersBut.clicked.connect(self.saveParameters)
        self.ui.loadParametersBut.clicked.connect(self.loadParameters)
        self.ui.detectSpikesBut.clicked.connect(self.detectSpikes)
        self.ui.verifySpikesBut.clicked.connect(self.verifySpikes)
        self.ui.applySVMBut.clicked.connect(self.applySVM)
        self.ui.applyContinuityBut.clicked.connect(self.applyContinuity)
        self.ui.detectTimestampsBut.clicked.connect(self.detectTimestamps)
        self.ui.verifyCorrectTimestampsBut.clicked.connect(self.verifyAndCorrect)

    def calcHilb(self):
        print('calcHilb')

        TSName = self.ui.loadTimeseriesLineEdit.text()
        hilbName = self.ui.saveHilbLineEdit.text()
        taps = self.ui.tapsLineEdit.text()
        gmeansize = self.ui.gmeanLineEdit.text()
        lowCutoff = self.ui.lowCutoffLineEdit.text()
        highCutoff = self.ui.highCutoffLineEdit.text()

        listArgs = ['--numtaps=%s'%(taps), \
                        '--gmeansize=%s'%(gmeansize), \
                        '--lowcutoff=%s'%(lowCutoff), \
                        '--highcutoff=%s'%(highCutoff), \
                        TSName, \
                        hilbName, \
                        ]

        dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        # Same name of self.dicProgram
        self.programname = 'calcHilb'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.calcHilbProgram.start('./../spikes/hilb', \
                                        listArgs)

        self.cancelled = False
        def calcHilbFinish(ret, exitStatus):
            self.app.restoreOverrideCursor()
            dialog.hide()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.ui.loadHilbLineEdit.setText(hilbName)
            else:
                return None

        self.calcHilbProgram.finished.connect(calcHilbFinish)
        self.calcHilbProgram.readyReadStandardOutput.connect(self.printAllStandardOutput)
        self.calcHilbProgram.readyReadStandardError.connect(self.printAllStandardError)

    def detectSpikes(self):
        print('spikes')
        TSName = self.ui.loadTimeseriesLineEdit.text()
        hilbName = self.ui.loadHilbLineEdit.text()
        saveSpikes = self.ui.saveSpikesLineEdit.text()
        locs_file = os.path.dirname(saveSpikes) +'/'+ os.path.basename(saveSpikes)+'_locs.npy'
        detection = self.ui.minHilbLineEdit.text()
        tolerance = self.ui.toleranceLineEdit.text()
        subsamp = self.ui.subsampLineEdit.text()
        minwavelet = self.ui.minWaveletLineEdit.text()
        maxwavelet = self.ui.maxWaveletLineEdit.text()
        stepwavelet = self.ui.stepWaveletLineEdit.text()
        argmaxorder = self.ui.peakLineEdit.text()
        taps = self.ui.tapsLineEdit.text()
        onlyAbove = self.ui.onlyAboveLineEdit.text()

        listArgs = ['--detection=%s'%detection, \
                            '--onlyabove=%s'%onlyAbove, \
                            '--tolerance=%s'%tolerance, \
                            '--subsamp=%s'%subsamp, \
                            '--minWavelet=%s'%minwavelet, \
                            '--maxWavelet=%s'%maxwavelet, \
                            '--stepWavelet=%s'%stepwavelet, \
                            '--argmaxorder=%s'%argmaxorder, \
                            TSName, \
                            hilbName, \
                            locs_file, \
                            saveSpikes]

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

        self.detectSpikesProgram.finished.connect(detectSpikesFinish)
        self.detectSpikesProgram.readyReadStandardOutput.connect(self.printAllStandardOutput)
        self.detectSpikesProgram.readyReadStandardError.connect(self.printAllStandardError)        
    
    def verifySpikes(self):
        print('winview')
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
                print('stdout:\n' + self.verifySpikesProgram.readAllStandardOutput().data().decode())
                print('stderr:\n' + self.verifySpikesProgram.readAllStandardError().data().decode())
                return None
        
        self.verifySpikesProgram.finished.connect(verifySpikesFinish)
    
    def applySVM(self):
        print('singlefish')
        minWin = self.ui.minWinLineEdit.text()
        onlyAbove = self.ui.onlyAboveLineEdit.text()
        lowSaturation = self.ui.lowSaturationLineEdit.text()
        highSaturation = self.ui.highSaturationLineEdit.text()
        TSName = self.ui.loadTimeseriesLineEdit.text()
        spikesName = self.ui.loadSpikesLineEdit.text()
        scaleName = self.ui.loadRescaleLineEdit.text()
        filterName = self.ui.loadFilterLineEdit.text()
        svmName = self.ui.loadSVMModelLineEdit.text()
        saveSinglefish = self.ui.saveSinglefishLineEdit.text()
        saveProb = self.ui.saveProbLineEdit.text()
        
        #winlen = max( (self.mean_stdWinLen(winLen1), self.mean_stdWinLen(winLen2)) )
        
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
                                    '--minprob=0.99', \
                                    TSName, \
                                    spikesName, \
                                    scaleName, \
                                    filterName, \
                                    svmName, \
                                    saveSinglefish, \
                                    saveProb])
        
        self.cancelled = False
        def applySVMFinish(ret, exitStatus):
            print('singlefish finished (%d,%s)'%(ret, repr(exitStatus)))
            self.app.restoreOverrideCursor()
            dialog.hide()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.ui.loadSinglefishLineEdit.setText(saveSinglefish)
                self.ui.loadProbLineEdit.setText(saveProb)
            else:
                print('stdout:\n' + self.applySVMProgram.readAllStandardOutput().data().decode())
                print('stderr:\n' + self.applySVMProgram.readAllStandardError().data().decode())
                return None
        
        self.applySVMProgram.finished.connect(applySVMFinish)
        self.applySVMProgram.readyReadStandardOutput.connect(self.printAllStandardOutput)
        self.applySVMProgram.readyReadStandardError.connect(self.printAllStandardError)
    
    def applyContinuity(self):
        print('recog')
        self.lowSaturation = self.ui.lowSaturationLineEdit.text()
        self.highSaturation = self.ui.highSaturationLineEdit.text()
        self.TSName = self.ui.loadTimeseriesLineEdit.text()
        self.hilbName = self.ui.loadHilbLineEdit.text()
        self.spikesName = self.ui.loadSpikesLineEdit.text()
        self.singlefishName = self.ui.loadSinglefishLineEdit.text()
        self.probName = self.ui.loadProbLineEdit.text()
        self.saveDBName = self.ui.saveDBLineEdit.text()
        self.TSoutput = '/tmp/' + self.saveDBName.split('/')[-1].split('.')[0] + '.timestamps'
       
        if os.path.isfile(self.saveDBName):
            dialog = QtWidgets.QMessageBox()
            dialog.setModal(True)
            dialog.setWindowTitle('Warning')
            dialog.setText('You want to override the original DB or apply over it?\n' + \
                           '(when applying over it, it will only substitute the spikes that' + \
                           'had euclidean distance inferior to the stored on the DB)')
            dialog.addButton(QtWidgets.QPushButton('Override'), QtWidgets.QMessageBox.YesRole) #0
            dialog.addButton(QtWidgets.QPushButton('Apply over'), QtWidgets.QMessageBox.NoRole) #1
            dialog.addButton(QtWidgets.QMessageBox.Cancel)
            
            ret = dialog.exec_()
            
            if ret == QtWidgets.QMessageBox.Cancel:
                return None
            elif ret == 0: #Override
                print('Removing DB file...')
                os.remove(self.saveDBName)
                recogdb.openDB(self.saveDBName, 'w')
            else: #ret == 1 -> Apply over
                pass
        else:
            recogdb.openDB(self.saveDBName, 'w')
        
        self.recogPassed = False
        self.recog(1)
    
    def recog(self, d):
        # TODO: saturation level??
        print('direction = %d'%d)
        
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
                                           self.hilbName, \
                                           self.spikesName, \
                                           self.singlefishName, \
                                           self.probName, \
                                           self.TSoutput])
        
        self.cancelled = False
        def recogFinish(ret, exitStatus):
            print('recog finished (%d,%s)'%(ret, repr(exitStatus)))
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
                print('stdout:\n' + self.applyContinuityProgram.readAllStandardOutput().data().decode())
                print('stderr:\n' + self.applyContinuityProgram.readAllStandardError().data().decode())
                return None
        
        
        self.applyContinuityProgram.finished.connect(recogFinish)
        self.applyContinuityProgram.readyReadStandardOutput.connect(self.printAllStandardOutput)
        self.applyContinuityProgram.readyReadStandardError.connect(self.printAllStandardError)
        
    
    def mean_stdWinLen(self, winlenFilename):
        data = np.loadtxt(str(winlenFilename))
        m = np.mean(data)
        s = np.std(data)
        return int(np.ceil(m+s))
    
    def detectTimestamps(self):
        print('detectIPI')
        DBName = self.ui.loadDBLineEdit.text()
        saveTimestamps = self.ui.saveTimestampsLineEdit.text()
        
        dialog = self.raiseLongTimeInformation()
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        self.programname = 'detectIPI'
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.detectTimestampsProgram.start('./../recog/recog', \
                                           ['export', \
                                            DBName, \
                                            saveTimestamps])
        
        self.cancelled = False
        def detectTimestampsFinish(ret, exitStatus):
            print('detectIPI finished (%d,%s)'%(ret, repr(exitStatus)))
            dialog.hide()
            self.app.restoreOverrideCursor()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                self.ui.loadTimestampsLineEdit.setText(saveTimestamps)
            else:
                print('stdout:\n' + self.detectSpikesProgram.readAllStandardOutput().data().decode())
                print('stderr:\n' + self.detectSpikesProgram.readAllStandardError().data().decode())
                return None
        
        self.detectTimestampsProgram.finished.connect(detectTimestampsFinish)
        self.detectTimestampsProgram.readyReadStandardOutput.connect(self.printAllStandardOutput)
        self.detectTimestampsProgram.readyReadStandardError.connect(self.printAllStandardError)
    
    def verifyAndCorrect(self):
        print('plotIPIandSVM')
        lowSaturation = float(self.ui.lowSaturationLineEdit.text())
        highSaturation = float(self.ui.highSaturationLineEdit.text())
        DBName = str(self.ui.loadDBLineEdit.text())
        timeseriesFile = self.ui.loadTimeseriesLineEdit.text()
        spikesFile = self.ui.loadSpikesLineEdit.text()
        timestampsFile = str(self.ui.loadTimestampsLineEdit.text())
        
        self.programname = 'plotIPIandSVM'
        
        timeseriesName = str(timeseriesFile.split('/')[-1].split('.')[0])
        if os.path.isdir(timeseriesName) == False:
            os.makedirs(str(timeseriesName))
        dbname = str(DBName.split('/')[-1].split('.')[0] + '_undo.keys')
        undoFilename = str(timeseriesName + '/' + dbname)
        open(undoFilename,'a').close()
        
        #Be sure that is on current directory
        os.chdir( os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) )
        self.plotIPIandSVMProgram.start('./../plotIPIandSVM/plotIPIandSVM', \
                                        [DBName, \
                                        timeseriesFile, \
                                        timestampsFile, \
                                        ])

        self.cancelled = False
        def plotIPIandSVMFinish(ret, exitStatus):
            self.app.restoreOverrideCursor()
            if (self.isReturnCodeOk(ret) is True) and (exitStatus == QtCore.QProcess.NormalExit) and (self.cancelled is False):
                pass
            else:
                print('error')
                return None

        self.plotIPIandSVMProgram.finished.connect(plotIPIandSVMFinish)
        self.plotIPIandSVMProgram.readyReadStandardOutput.connect(self.printAllStandardOutput)
        self.plotIPIandSVMProgram.readyReadStandardError.connect(self.printAllStandardError)


        
    def printAllStandardOutput(self):
        #print('%s\n'%self.programname)
        for program in self.dicProgram[self.programname]:
            if sys.version_info.major == 3:
                sys.stdout.write(program.readAllStandardOutput().data().decode())
            else:
                sys.stdout.write(program.readAllStandardOutput().data().decode())
            sys.stdout.flush()
    
    def printAllStandardError(self):
        #print('%s\n'%self.programname)
        for program in self.dicProgram[self.programname]:
            if sys.version_info.major == 3:
                sys.stderr.write(program.readAllStandardError().data().decode())
            else:
                sys.stderr.write(program.readAllStandardError().data())
            sys.stderr.flush()
    
    def raiseLongTimeInformation(self):
        dialog = QtWidgets.QMessageBox()
        dialog.setWindowTitle('Information')
        dialog.setText("This may take a while...\nTime for a coffee!\n")
        dialog.setModal(True)
        self.CancelBut = dialog.addButton(QtWidgets.QMessageBox.Cancel)
        self.CancelBut.clicked.connect(self.cancelApp)
        dialog.show()
        return dialog
    
    def cancelApp(self):
        print('Cancelled.')
        self.cancelled = True
        self.app.restoreOverrideCursor()
        for l in self.dicProgram.values():
            for program in l:
                program.close()
    
    def isReturnCodeOk(self, ret):
        if ret != 0:
            print('\n---\tERROR (%s): %d\t---\n'%(self.programname, ret))
            for program in self.dicProgram[self.programname]:
                print(program.readAllStandardOutput().data().decode())
                print(program.readAllStandardError().data().decode())
            self.raiseParameterError('%s ERROR!\n'%self.programname)
            return False
        else:
            return True
    
    def raiseParameterError(self, text):
        QtWidgets.QMessageBox.critical(self, "ERROR", text + "Please check your parameters.", QtWidgets.QMessageBox.Ok )
    
    def saveParameters(self):
        saveFilename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Parameters File', '', 'Parameters File (*.discparameters) (*.discparameters);;All files (*.*) (*.*)')
        if saveFilename[0] != u'':
            saveFile = open(saveFilename[0], 'w')
            for element in self.lineFieldsList:
                if isinstance(element, QtWidgets.QLineEdit):
                    saveFile.write( '%s\t%s\n'%(element.objectName(), element.text()) )
            saveFile.close()

    def loadParameters(self):
        loadFilename = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Parameters File', '', 'Parameters File (*.discparameters) (*.discparameters);;All files (*.*) (*.*)')
        if loadFilename[0] != u'':
            loadFile = open(loadFilename[0], 'r')
            for line in loadFile.readlines():
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
            if isinstance(layout, QtWidgets.QLayout):
                for i in xrange(layout.count()):
                    try:
                        layout.itemAt(i).widget().hide()
                    except:
                        pass
            elif isinstance(layout, QtWidgets.QWidget):
                layout.hide()
        
        else:
            label.setText( label.text()[:-2] + ' >' )
            if isinstance(layout, QtWidgets.QLayout):
                for i in xrange(layout.count()):
                    try:
                        layout.itemAt(i).widget().show()
                    except:
                        pass
            elif isinstance(layout, QtWidgets.QWidget):
                layout.show()

        self.isLayoutShown[idx] = not(self.isLayoutShown[idx])
    
    def defineFieldsType(self):
        self.fieldsType = {self.ui.loadTimeseriesLineEdit: 'load', \
                           self.ui.saveHilbLineEdit: 'save', \
                           self.ui.loadHilbLineEdit: 'load', \

                           self.ui.lowSaturationLineEdit: 'float', \
                           self.ui.highSaturationLineEdit: 'float', \
                           self.ui.gmeanLineEdit: 'int', \
                           self.ui.tapsLineEdit: 'int', \
                           self.ui.lowCutoffLineEdit: 'float', \
                           self.ui.highCutoffLineEdit: 'float', \

                           self.ui.subsampLineEdit: 'int', \
                           self.ui.minWaveletLineEdit: 'float', \
                           self.ui.maxWaveletLineEdit: 'float', \
                           self.ui.stepWaveletLineEdit: 'float', \
                           self.ui.peakLineEdit: 'int', \
                           self.ui.minHilbLineEdit: 'float', \
                           self.ui.toleranceLineEdit: 'float', \

                           self.ui.saveSpikesLineEdit: 'save', \
                           
                           self.ui.loadSpikesLineEdit: 'load', \
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
            self.ui.saveHilbLineEdit: 'Hilbert transform (*.hilb) (*.hilb)', \
            self.ui.loadHilbLineEdit: 'Hilbert transform (*.hilb) (*.hilb)', \
            self.ui.saveSpikesLineEdit: 'Spikes File (*.spikes) (*.spikes)', \
            self.ui.loadSpikesLineEdit: 'Spikes File (*.spikes) (*.spikes)', \
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
        fileFilter = QString(self.fileFieldsExtension[field]) + QString(';;All files (*.*) (*.*)')
        if self.fieldsType[field] == 'load':
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Load file', path, fileFilter)
        elif self.fieldsType[field] == 'save':
            filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', path, fileFilter )
        
        if filename != '':
            field.setText(filename[0])
        else:
            pass
    
    def connectFileFields(self):
        FileFields = (self.ui.loadTimeseriesLineEdit, \
                      self.ui.saveHilbLineEdit, \
                      self.ui.loadHilbLineEdit, \
                      self.ui.saveSpikesLineEdit, \
                      self.ui.loadSpikesLineEdit, \
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
            field.clicked.connect(self.fileFieldHandler)
    
    def connectUnlockFields(self):
        
        # The first element of the unlockers is the list of fields that block others
        # The second element are the fields that are release by that edition

        self.hilbParametersUnlocker = ( \
            ( \
                (self.ui.loadTimeseriesLineEdit, \
                self.ui.gmeanLineEdit, \
                self.ui.tapsLineEdit, \
                self.ui.lowCutoffLineEdit, \
                self.ui.highCutoffLineEdit, \
                ), \
                (self.ui.saveHilbLineEdit, \
                )
            ), \
            ( \
                (self.ui.loadTimeseriesLineEdit, \
                self.ui.gmeanLineEdit, \
                self.ui.tapsLineEdit, \
                self.ui.lowCutoffLineEdit, \
                self.ui.highCutoffLineEdit, \
                self.ui.saveHilbLineEdit, \
                ), \
                (self.ui.calcHilbBut, \
                )
            ), \
        )

        self.spikeParametersUnlocker = ( \
            ( \
                (self.ui.loadHilbLineEdit, \
                 self.ui.subsampLineEdit, \
                 self.ui.peakLineEdit, \
                 self.ui.minWaveletLineEdit, \
                 self.ui.maxWaveletLineEdit, \
                 self.ui.stepWaveletLineEdit, \
                 self.ui.minHilbLineEdit, \
                 self.ui.toleranceLineEdit, \
                ), \
                (self.ui.saveSpikesLineEdit, \
                )
            ), \
            ( \
                (self.ui.loadHilbLineEdit, \
                 self.ui.subsampLineEdit, \
                 self.ui.peakLineEdit, \
                 self.ui.minWaveletLineEdit, \
                 self.ui.maxWaveletLineEdit, \
                 self.ui.stepWaveletLineEdit, \
                 self.ui.minHilbLineEdit, \
                 self.ui.toleranceLineEdit, \
                 self.ui.saveSpikesLineEdit, \
                ), \
                (self.ui.detectSpikesBut, \
                )
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
                 self.ui.loadHilbLineEdit, \
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
        self.Fields = {self.ui.loadTimeseriesLineEdit: self.hilbParametersUnlocker, \
                       self.ui.saveHilbLineEdit: self.hilbParametersUnlocker, \
                       self.ui.lowSaturationLineEdit: self.SVMSaveParametersUnlocker, \
                       self.ui.highSaturationLineEdit: self.SVMSaveParametersUnlocker, \
                       self.ui.gmeanLineEdit: self.hilbParametersUnlocker, \
                       self.ui.tapsLineEdit: self.hilbParametersUnlocker, \
                       self.ui.lowCutoffLineEdit: self.hilbParametersUnlocker, \
                       self.ui.highCutoffLineEdit: self.hilbParametersUnlocker, \
                       self.ui.loadHilbLineEdit: self.spikeParametersUnlocker, \
                       self.ui.subsampLineEdit: self.spikeParametersUnlocker, \
                       self.ui.peakLineEdit: self.spikeParametersUnlocker, \
                       self.ui.minWaveletLineEdit: self.spikeParametersUnlocker, \
                       self.ui.maxWaveletLineEdit: self.spikeParametersUnlocker, \
                       self.ui.stepWaveletLineEdit: self.spikeParametersUnlocker, \
                       self.ui.minHilbLineEdit: self.spikeParametersUnlocker, \
                       self.ui.toleranceLineEdit: self.spikeParametersUnlocker, \
                       self.ui.saveSpikesLineEdit: self.spikeParametersUnlocker, \
                       self.ui.loadSpikesLineEdit: self.SVMLoadParametersUnlocker, \
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
            if isinstance(field, QtWidgets.QLineEdit):
                field.textChanged.connect(self.tryUnlock)
            elif isinstance(field, QtWidgets.QCheckBox):
                field.stateChanged.connect(self.tryUnlock)
    
    def initialClickState(self):
        for field in self.Fields.keys():
            tup = self.Fields[field]
            print(field.objectName())
            for locker,locked in tup:
                self.switchLockState(locked, False)
    
    def tryUnlockRaw(self, field):
        for tup in self.Fields[field]:
            allChecked = True
            for f in tup[0]:
                allChecked = allChecked and self.verifyField(f)

            self.switchLockState(tup[1], allChecked)

    def tryUnlock(self, text):
        field = self.sender()

        self.tryUnlockRaw(field)
    
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

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    
    myapp = DiscriminateWindow(app)
    
    myapp.show()
    sys.exit(app.exec_())
