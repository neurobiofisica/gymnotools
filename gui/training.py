import sys

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
                self.ui.step4ParametersLayout, \
                self.ui.step5ParametersLayout, \
                ]

        self.titleLabels = [self.ui.step1TitleLabel, \
                self.ui.step2TitleLabel, \
                self.ui.step3TitleLabel, \
                self.ui.step4TitleLabel, \
                self.ui.step5TitleLabel, \
                ]

        self.defineClickableLists()
        self.initialClickState()

        # TODO: Pensar melhor de acordo com os lockers
        self.isLayoutShown = [False, \
        False, \
        False, \
        False, \
        False, \
        ]
        for layout in self.ParametersLayout:
            for i in xrange(layout.count()):
                try:
                    layout.itemAt(i).widget().hide()
                except:
                    pass
        
        for label in self.titleLabels:
            QtCore.QObject.connect(label, QtCore.SIGNAL('clicked()'), self.expandLayout)
    
    def defineClickableLists(self):
        # Load Timeseries locker
        self.loadTSFish1Locker = [self.ui.lowSaturation1LineEdit, \
                                  self.ui.highSaturation1LineEdit, \
                                  self.ui.taps1LineEdit, \
                                  self.ui.cutoff1LineEdit, \
                                  self.ui.thresholdLevel1LineEdit, \
                                  self.ui.thresholdAssist1But, \
                                  self.ui.filterAssist1But, \
                                  ]
        self.loadTSFish2Locker = [self.ui.lowSaturation2LineEdit, \
                                  self.ui.highSaturation2LineEdit, \
                                  self.ui.taps2LineEdit, \
                                  self.ui.cutoff2LineEdit, \
                                  self.ui.thresholdLevel2LineEdit, \
                                  self.ui.thresholdAssist2But, \
                                  self.ui.filterAssist2But, \
                                  ]
        
        # Spike parameters locker
        self.spikeParametersFish1Locker = [self.ui.saveSpikes1LineEdit, \
                                           self.ui.saveWindowLengths1LineEdit, \
                                           ]
        self.spikeParametersFish2Locker = [self.ui.saveSpikes2LineEdit, \
                                           self.ui.saveWindowLengths2LineEdit, \
                                          ]
        
        # Spike savefiles locker
        self.spikeSavefilesFish1Locker = [self.ui.detectSpikes1But, \
                                          ]
        self.spikeSavefilesFish2Locker = [self.ui.detectSpikes2But, \
                                          ]
        
        # Load Spikes locker
        self.loadSpikesFish1Locker = [self.ui.verifySpikes1But, \
                                      ]
        self.loadSpikesFish2Locker = [self.ui.verifySpikes2But, \
                                      ]
        self.loadSpikesBothLocker = [self.ui.saveFeatures1LineEdit, \
                                     self.ui.saveFeatures2LineEdit, \
                                     self.ui.saveFilterLineEdit, \
                                     self.ui.numberFeaturesLineEdit, \
                                     ]
        
        # Features parameters locker
        self.featuresParametersLocker = [self.ui.extractFeaturesBut, \
                                      ]
        
        # Load Features locker
        self.loadFeaturesLocker = [self.ui.trainingNumberSamplesLineEdit, \
                                   self.ui.crossNumberSamplesLineEdit, \
                                   self.ui.testingNumberSamplesLineEdit, \
                                   
                                   self.ui.trainingProbabilityLineEdit, \
                                   self.ui.crossProbabilityLineEdit, \
                                   self.ui.testingProbabilityLineEdit, \
                                   
                                   self.ui.trainingSaveLineEdit, \
                                   self.ui.crossSaveLineEdit, \
                                   self.ui.testingSaveLineEdit, \
                                   ]
        
        # Slice Parameters locker
        self.sliceParametersLocker = [self.ui.sliceBut, \
                                      ]
        
        # Load Slice locker
        self.loadSliceLocker = [self.ui.defaultValuesBut, \
                                self.ui.cStartLineEdit, \
                                self.ui.cStepLineEdit, \
                                self.ui.cStopLineEdit, \
                                self.ui.cValueLineEdit, \
                                self.ui.gStartLineEdit, \
                                self.ui.gStepLineEdit, \
                                self.ui.gStopLineEdit, \
                                self.ui.gValueLineEdit, \
                                ]
        
        # SVM Grid Values locker
        self.SVMGridValuesLocker = [self.ui.optimizeSVMBut, \
                                    ]
        
        # SVM Parameters locker
        self.SVMParametersLocker = [self.ui.saveSVMLineEdit, \
                                    ]
        
        # Save SVM locker
        self.saveSVMLocker = [self.ui.trainSVMBut, \
                              ]
        
        # Testing set and SVM locker (ROC curve)
        self.testingAndSVMLocker = [self.ui.generateROCBut, \
                                    ]
        
    def switchLockState(self, lockerList, state):
        for el in lockerList:
            el.setEnabled(False)
    
    def initialClickState(self):
        # Step 1 LineEdits
        self.switchLockState(self.loadTSFish1Locker, False)
        self.switchLockState(self.loadTSFish2Locker, False)
        self.switchLockState(self.spikeParametersFish1Locker, False)
        self.switchLockState(self.spikeParametersFish2Locker, False)
        self.switchLockState(self.spikeSavefilesFish1Locker, False)
        self.switchLockState(self.spikeSavefilesFish2Locker, False)
        self.switchLockState(self.loadSpikesFish1Locker, False)
        self.switchLockState(self.loadSpikesFish2Locker, False)
        self.switchLockState(self.loadSpikesBothLocker, False)
        self.switchLockState(self.featuresParametersLocker, False)
        self.switchLockState(self.loadFeaturesLocker, False)
        self.switchLockState(self.sliceParametersLocker, False)
        self.switchLockState(self.loadSliceLocker, False)
        self.switchLockState(self.SVMGridValuesLocker, False)
        self.switchLockState(self.SVMParametersLocker, False)
        self.switchLockState(self.saveSVMLocker, False)
        self.switchLockState(self.testingAndSVMLocker, False)
        

    def expandLayout(self):

        label = self.sender()
        idx = self.titleLabels.index(label)
        layout = self.ParametersLayout[idx]

        if self.isLayoutShown[idx]:
            label.setText( label.text()[:-2] + ' v' )
            for i in xrange(layout.count()):
                try:
                    layout.itemAt(i).widget().hide()
                except:
                    pass
        else:
            label.setText( label.text()[:-2] + ' >' )
            for i in xrange(layout.count()):
                try:
                    layout.itemAt(i).widget().show()
                except:
                    pass

        self.isLayoutShown[idx] = not(self.isLayoutShown[idx])
        

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    myapp = TrainingWindow(app)

    myapp.show()
    sys.exit(app.exec_())
