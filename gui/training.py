import os, sys, subprocess

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
        
        self.connectFileFields(self.fileFieldHandler)
        self.connectUnlockFields()
        self.connectButtons()
        
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
    
    def filterAssist1(self):
        TSName = self.ui.loadTS1LineEdit.text()
        
        try:
            out = subprocess.check_output(['./../paramchooser/paramchooser', 'lowpass', TSName], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print '\n---\tERROR!\t---\n'
            print e.returncode
            
        numtaps = out.split('numtaps = ')[1].split('\n')[0]
        cutoff = out.split('cutoff = ')[1].split('\n')[0]
        
        self.ui.taps1LineEdit.setText(numtaps)
        self.ui.cutoff1LineEdit.setText(cutoff)
    
    def filterAssist2(self):
        TSName = self.ui.loadTS2LineEdit.text()
        
        try:
            out = subprocess.check_output(['./../paramchooser/paramchooser', 'lowpass', TSName], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print '\n---\tERROR!\t---\n'
            print e.returncode
            
        numtaps = out.split('numtaps = ')[1].split('\n')[0]
        cutoff = out.split('cutoff = ')[1].split('\n')[0]
        
        self.ui.taps2LineEdit.setText(numtaps)
        self.ui.cutoff2LineEdit.setText(cutoff)
    
    def thresholdAssist1(self):
        TSName = self.ui.loadTS1LineEdit.text()
        taps = self.ui.taps1LineEdit.text()
        cutoff = self.ui.cutoff1LineEdit.text()
        
        try:
            out = subprocess.check_output(['./../paramchooser/paramchooser', 'threshold', TSName, taps, cutoff], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print '\n---\tERROR!\t---\n'
            print e.returncode
        
        threshold = out.split('threshold = ')[1].split('\n')[0]
        self.ui.thresholdLevel1LineEdit.setText(threshold)
    
    def thresholdAssist2(self):
        TSName = self.ui.loadTS2LineEdit.text()
        taps = self.ui.taps2LineEdit.text()
        cutoff = self.ui.cutoff2LineEdit.text()
        
        try:
            out = subprocess.check_output(['./../paramchooser/paramchooser', 'threshold', TSName, taps, cutoff], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print '\n---\tERROR!\t---\n'
            print e.returncode
        
        threshold = out.split('threshold = ')[1].split('\n')[0]
        self.ui.thresholdLevel2LineEdit.setText(threshold)
    
    def verifySpikes1(self):
        spikesName = self.ui.loadSpikes1LineEdit.text()
        TSName = self.ui.loadTS1LineEdit.text()
        
        try:
            if TSName != '':
                out = subprocess.check_output(['./../winview/winview', spikesName, TSName], stderr=subprocess.STDOUT)
            else:
                out = subprocess.check_output(['./../winview/winview', spikesName], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print '\n---\tERROR!\t---\n'
            print e.returncode
    
    def verifySpikes2(self):
        spikesName = self.ui.loadSpikes2LineEdit.text()
        TSName = self.ui.loadTS2LineEdit.text()
        
        try:
            if TSName != '':
                out = subprocess.check_output(['./../winview/winview', spikesName, TSName], stderr=subprocess.STDOUT)
            else:
                out = subprocess.check_output(['./../winview/winview', spikesName], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print '\n---\tERROR!\t---\n'
            print e.returncode
    
    def detectSpikes1(self):
        TSName = self.ui.loadTS1LineEdit.text()
        lowSat = self.ui.lowSaturation1LineEdit.text()
        highSat = self.ui.highSaturation1LineEdit.text()
        taps = self.ui.taps1LineEdit.text()
        cutoff = self.ui.cutoff1LineEdit.text()
        threshold = self.ui.thresholdLevel1LineEdit.text()
        saveSpikes = self.ui.saveSpikes1LineEdit.text()
        saveWindowLengths = self.ui.saveWindowLengths1LineEdit.text()
        
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            out = subprocess.check_output(['./../spikes/spikes', \
                                           '--fixedwin', \
                                           '--saturation=%s,%s'%(lowSat,highSat), \
                                           '--numtaps=%s'%taps, \
                                           '--cutoff=%s'%cutoff, \
                                           '--detection=%s'%threshold, \
                                           '--winlen=%s'%saveWindowLengths, \
                                           TSName, \
                                           saveSpikes], \
                                          stderr=subprocess.STDOUT)
            
            self.ui.loadSpikes1LineEdit.setText(saveSpikes)
        except subprocess.CalledProcessError as e:
            print '\n---\tERROR!\t---\n'
            print e.returncode
        self.app.restoreOverrideCursor()
    
    def detectSpikes2(self):
        TSName = self.ui.loadTS2LineEdit.text()
        lowSat = self.ui.lowSaturation2LineEdit.text()
        highSat = self.ui.highSaturation2LineEdit.text()
        taps = self.ui.taps2LineEdit.text()
        cutoff = self.ui.cutoff2LineEdit.text()
        threshold = self.ui.thresholdLevel2LineEdit.text()
        saveSpikes = self.ui.saveSpikes2LineEdit.text()
        saveWindowLengths = self.ui.saveWindowLengths2LineEdit.text()
        
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            out = subprocess.check_output(['./../spikes/spikes', \
                                           '--fixedwin', \
                                           '--saturation=%s,%s'%(lowSat,highSat), \
                                           '--numtaps=%s'%taps, \
                                           '--cutoff=%s'%cutoff, \
                                           '--detection=%s'%threshold, \
                                           '--winlen=%s'%saveWindowLengths, \
                                           TSName, \
                                           saveSpikes], \
                                          stderr=subprocess.STDOUT)
            
            self.ui.loadSpikes2LineEdit.setText(saveSpikes)
        except subprocess.CalledProcessError as e:
            print '\n---\tERROR!\t---\n'
            print e.returncode
        self.app.restoreOverrideCursor()
    
    def extractFeatures(self):
        spikesName1 = self.ui.loadSpikes1LineEdit.text()
        spikesName2 = self.ui.loadSpikes2LineEdit.text()
        unfilteredFeaturesName1 = self.ui.saveFeatures1LineEdit.text() + '_unfiltered'
        unfilteredFeaturesName2 = self.ui.saveFeatures2LineEdit.text() + '_unfiltered'
        featuresName1 = self.ui.saveFeatures1LineEdit.text()
        featuresName2 = self.ui.saveFeatures2LineEdit.text()
        filterName = self.ui.saveFilterLineEdit.text()
        rescaleName = self.ui.saveRescaleLineEdit.text()
        number = self.ui.numberFeaturesLineEdit.text()
        
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        # features compute
        print '\nfeatures compute'
        try:
            compute1 = subprocess.Popen(['./../features/features', \
                                           'compute', \
                                           spikesName1, \
                                           unfilteredFeaturesName1], \
                                          stderr=subprocess.STDOUT, \
                                          stdout=subprocess.PIPE)
            compute2 = subprocess.Popen(['./../features/features', \
                                           'compute', \
                                           spikesName2, \
                                           unfilteredFeaturesName2], \
                                          stderr=subprocess.STDOUT, \
                                          stdout=subprocess.PIPE)
            
            while (compute1.poll() is None) or (compute2.poll() is None):
                out = compute1.stdout.readline()
                if out != '':
                    print 'features compute file1: %s'%out
                out = compute2.stdout.readline()
                if out != '':
                    print 'features compute file2: %s'%out
                    
        except subprocess.CalledProcessError as e:
            print '\n---\tfeatures compute ERROR!\t---\n'
            print e.returncode
            return None
        
        # features rescale prepare
        print '\nfeatures rescale prepare'
        try:
            rescalePrepare = subprocess.Popen(['./../features/features', \
                                                'rescale', \
                                                'prepare', \
                                                rescaleName, \
                                                unfilteredFeaturesName1, \
                                                unfilteredFeaturesName2], \
                                               stderr=subprocess.STDOUT, \
                                               stdout=subprocess.PIPE)
            
            while rescalePrepare.poll() is None:
                out = rescalePrepare.stdout.readline()
                if out != '':
                    print 'features rescale prepare: %s'%out
        
        except subprocess.CalledProcessError as e:
            print '\n---\tfeatures rescale prepare ERROR!\t---\n'
            print e.returncode
            return None
        
        # features rescale apply
        print '\nfeatures rescale apply'
        try:
            rescaleApply = subprocess.Popen(['./../features/features', \
                                                'rescale', \
                                                'apply', \
                                                rescaleName, \
                                                unfilteredFeaturesName1, \
                                                unfilteredFeaturesName2], \
                                               stderr=subprocess.STDOUT, \
                                               stdout=subprocess.PIPE)
            
            while rescaleApply.poll() is None:
                out = rescaleApply.stdout.readline()
                if out != '':
                    print 'features rescale apply: %s'%out
        
        except subprocess.CalledProcessError as e:
            print '\n---\tfeatures rescale apply ERROR!\t---\n'
            print e.returncode
            return None
        
        # features filter prepare
        print '\nfeatures filter prepare'
        try:
            filterPrepare = subprocess.Popen(['./../features/features', \
                                                'filter', \
                                                'prepare', \
                                                '--best=%s'%number, \
                                                filterName, \
                                                unfilteredFeaturesName1, \
                                                unfilteredFeaturesName2], \
                                               stderr=subprocess.STDOUT, \
                                               stdout=subprocess.PIPE)
            
            while filterPrepare.poll() is None:
                out = filterPrepare.stdout.readline()
                if out != '':
                    print 'features filter prepare: %s'%out
        
        except subprocess.CalledProcessError as e:
            print '\n---\tfeatures filter prepare ERROR!\t---\n'
            print e.returncode
            return None
        
        # features filter apply
        print '\nfeatures filter apply'
        try:
            filterApply1 = subprocess.Popen(['./../features/features', \
                                                'filter', \
                                                'apply', \
                                                filterName, \
                                                unfilteredFeaturesName1, \
                                                featuresName1], \
                                               stderr=subprocess.STDOUT, \
                                               stdout=subprocess.PIPE)
            
            filterApply2 = subprocess.Popen(['./../features/features', \
                                                'filter', \
                                                'apply', \
                                                filterName, \
                                                unfilteredFeaturesName2, \
                                                featuresName2], \
                                               stderr=subprocess.STDOUT, \
                                               stdout=subprocess.PIPE)
            
            while (filterApply1.poll() is None) or (filterApply2.poll() is None):
                out = filterApply1.stdout.readline()
                if out != '':
                    print 'features filter apply file1: %s'%out
                out = filterApply2.stdout.readline()
                if out != '':
                    print 'features filter apply file2: %s'%out
        
        except subprocess.CalledProcessError as e:
            print '\n---\tfeatures filter apply ERROR!\t---\n'
            print e.returncode
            return None
        
        print '\nend features'
        self.ui.loadFeatures1LineEdit.setText(featuresName1)
        self.ui.loadFeatures2LineEdit.setText(featuresName2)
        self.app.restoreOverrideCursor()
    
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
                self.ui.testingNumberSamplesFish1LineEdit, \
                
                self.ui.trainingProbabilityFish1LineEdit, \
                self.ui.crossProbabilityFish1LineEdit, \
                self.ui.testingProbabilityFish1LineEdit, \
                
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
                self.ui.testingNumberSamplesFish2LineEdit, \
                
                self.ui.trainingProbabilityFish2LineEdit, \
                self.ui.crossProbabilityFish2LineEdit, \
                self.ui.testingProbabilityFish2LineEdit, \
                
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
        # Step 1 LineEdits
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
