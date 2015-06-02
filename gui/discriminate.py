import os, sys

from PyQt4 import QtCore, QtGui
from discriminate_interface import Ui_discriminateWindow

class DiscriminateWindow(QtGui.QDialog):
    def __init__(self, app, parent=None):
        self.app = app
        
        QtGui.QWidget.__init__(self)
        self.setFocusPolicy( QtCore.Qt.StrongFocus )
        self.setFocus()
        
        self.showMaximized()
        
        self.ui = Ui_discriminateWindow()
        self.ui.setupUi(self)
        
        # LineFields List -> for saving parameters
        self.lineFieldsList = (self.ui.loadTimeseriesLineEdit, \
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
                               self.ui.loadSinglefishLineEdit, \
                               self.ui.loadProbLineEdit, \
                               self.ui.saveDBLineEdit, \
                               self.ui.loadDBLineEdit, \
                               self.ui.saveTimestampsLineEdit, \
                               self.ui.loadTimestampsLineEdit, \
                               )
        
        self.ParametersLayout = (self.ui.step1ParametersLayout, \
                            self.ui.step2ParametersLayout, \
                            self.ui.step3ParametersLayout, \
                            self.ui.step4ParametersLayout, \
                            )
        
        self.titleLabels = (self.ui.step1TitleLabel, \
                            self.ui.step2TitleLabel, \
                            self.ui.step3TitleLabel, \
                            self.ui.step4TitleLabel, \
                            )
        
        self.isLayoutShown = [True, \
                             True, \
                             True, \
                             True, 
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
    
    def connectButtons(self):
        QtCore.QObject.connect(self.ui.saveParametersBut, QtCore.SIGNAL('clicked()'), self.saveParameters)
        QtCore.QObject.connect(self.ui.loadParametersBut, QtCore.SIGNAL('clicked()'), self.loadParameters)
    
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
                (self.ui.lowSaturationLineEdit, \
                 self.ui.highSaturationLineEdit, \
                 self.ui.tapsLineEdit, \
                 self.ui.cutoffLineEdit, \
                 self.ui.filterAssistBut, \
                ) \
            ), \
        )
        
        self.spikeParametersUnlocker = ( \
            ( \
                (self.ui.lowSaturationLineEdit, \
                 self.ui.highSaturationLineEdit, \
                 self.ui.tapsLineEdit, \
                 self.ui.cutoffLineEdit, \
                 self.ui.thresholdLevelLineEdit, \
                ), \
                (self.ui.saveSpikesLineEdit, \
                ) \
            ), \
            ( \
                (self.ui.tapsLineEdit, \
                 self.ui.cutoffLineEdit, \
                ), \
                (self.ui.thresholdLevelLineEdit, \
                 self.ui.thresholdAssistBut, \
                )
            ), \
        )
        
        self.spikeSavefileUnlocker = ( \
            ( \
                (self.ui.saveSpikesLineEdit, \
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
                (self.ui.loadSpikesLineEdit, \
                 self.ui.loadWinlen1LineEdit, \
                 self.ui.loadWinlen2LineEdit, \
                 self.ui.loadFilterLineEdit, \
                 self.ui.loadRescaleLineEdit, \
                 self.ui.loadSVMModelLineEdit, \
                ), \
                (self.ui.saveSinglefishLineEdit, \
                 self.ui.saveProbLineEdit, \
                )
            ), \
        )
        
        self.SVMSaveParametersUnlocker = ( \
            ( \
                (self.ui.saveSinglefishLineEdit, \
                 self.ui.saveProbLineEdit, \
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
                (self.ui.saveDBLineEdit, \
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
                (self.ui.saveTimestampsLineEdit, \
                ), \
                (self.ui.detectTimestampsBut, \
                )
            ), \
        )
        
        self.loadTimestampsUnlocker = ( \
            ( \
                (self.ui.loadTimestampsLineEdit, \
                ), \
                (self.ui.verifyCorrectTimestampsBut, \
                )
            ), \
        )
        
        # Connects each field to its unlocker (dependencies and unlockers)
        self.Fields = {self.ui.loadTimeseriesLineEdit: self.loadTimeseriesUnlocker, \
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
                       self.ui.loadSinglefishLineEdit: self.loadContinuityParametersUnlocker, \
                       self.ui.loadProbLineEdit: self.loadContinuityParametersUnlocker, \
                       self.ui.saveDBLineEdit: self.saveDBUnlocker, \
                       self.ui.loadDBLineEdit: self.loadDBUnlocker, \
                       self.ui.saveTimestampsLineEdit: self.saveTimestampsUnlocker, \
                       self.ui.loadTimestampsLineEdit: self.loadTimestampsUnlocker, \
                       }
        
        for field in self.Fields.keys():
            QtCore.QObject.connect(field, QtCore.SIGNAL('textChanged(QString)'), self.tryUnlock)
    
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
            
        else:
            if data != '':
                return True
            else:
                return False
    
    def switchLockState(self, lockerList, state):
        for el in lockerList:
            el.setEnabled(state)

if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)
    
    myapp = DiscriminateWindow(app)
    
    myapp.show()
    sys.exit(app.exec_())