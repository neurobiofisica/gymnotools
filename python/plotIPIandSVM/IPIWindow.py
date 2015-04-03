from PyQt4 import QtCore, QtGui
from IPIClick_interface import *

import numpy as np

import sys, os
sys.path.append( os.path.realpath('../') )
import recogdb

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

INVERTION = 0

dicUndo = {INVERTION: 'Continuity invertion\n',
}

class ModifySelector:
    def __init__(self, db, undoFilename, folder):
        self.db = db
        self.undoFilename = undoFilename
        self.folder = folder
        self.undoKeys = set(np.loadtxt(undoFilename, unpack=True))
        
        self.replot = False

    # undoList = [ ( Action, {Fields: (Old, New)} ), ( Action, {Fields: (Old, New)} ), ... ]
    def parseModifications(self, key):
        modFilename = self.folder + '/' + str(key) + '.undo'
        if not os.path.isfile(modFilename):
            return None
        modFile = open(modFilename, 'r')
        
        undoList = []
        ActionNow = ''
        dicActions = {}
        for l in modFile.xreadlines():
            Columns = l.split('\t')
            
            # Action identifier
            if Columns[0] != '':
                if len(dicActions.keys()) != 0:
                    undoList.append( (ActionNow, dicActions) ) 
                    
                ActionNow = Columns[0]
                assert ( ActionNow in dicUndo.values() )
                dicActions = {}
                continue
            
            # Field identifier
            Field = Columns[1].strip()
            OldValue = Columns[2].strip()
            NewValue = Columns[3].strip()
            
            assert ( Field in recogdb.dicFields.keys() )
            
            dicActions[Field] = (OldValue, NewValue)
           
        # Append last action 
        undoList.append( (ActionNow, dicActions) ) 
        return undoList

    def invertIPI(self, key):
        if key not in self.undoKeys:
            undoFile = open(self.undoFilename, 'a')
            undoFile.write('%d\n'%key)
            undoFile.flush()
            undoFile.close()
        
        keyundofile = open(self.folder + '/' + str(key) + '.undo', 'a')
        
        off, read_data, spkdata = recogdb.readHeaderEntry(self.db, key)
        
        # Store old SVM data on DB (it will change to 'm' - Manually)
        oldSVM = read_data[ recogdb.dicFields['svm'] ]
        
        # Store old 'presentFish' data
        oldFish = read_data[ recogdb.dicFields['presentFish'] ]
        if oldFish not in (1,2):
            print 'only single spikes can be inverted'
            return None
        newFish = 2 if oldFish == 1 else 1
        
        # Store old correctedPos data - The fields must be inverted
        oldCorrectedPosA = read_data[ recogdb.dicFields['correctedPosA'] ]
        oldCorrectedPosB = read_data[ recogdb.dicFields['correctedPosB'] ]
        if newFish == 1:
            newCorrectedPosA = oldCorrectedPosB
            newCorrectedPosB = -1
        else:
            newCorrectedPosA = -1
            newCorrectedPosB = oldCorrectedPosA
        
        # Store the old dists fields - They are put to a minimum acording the the fish
        # So the continuity will no overwrite them
        oldDistA = read_data[ recogdb.dicFields['distA'] ]
        oldDistB = read_data[ recogdb.dicFields['distB'] ]
        oldDistAB = read_data[ recogdb.dicFields['distAB'] ]
        if newFish == 1:
            newDistA = 0.
            newDistB = float('Inf')
            newDistAB = float('Inf')
        else:
            newDistA = float('Inf')
            newDistB = 0.
            newDistAB = float('Inf')
        
        
        # Update DB
        recogdb.updateHeaderEntry(self.db, key, 'presentFish', newFish, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'correctedPosA', newCorrectedPosA, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'correctedPosB', newCorrectedPosB, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'distA', newDistA, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'distB', newDistB, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'distAB', newDistAB, sync=True)
        
        off, new_data, spkdata = recogdb.readHeaderEntry(self.db, key)
        
        newSVM = new_data[ recogdb.dicFields['svm'] ]
        newFish = new_data[ recogdb.dicFields['presentFish'] ]
        newCorrectedPosA = read_data[ recogdb.dicFields['correctedPosA'] ]
        newCorrectedPosB = read_data[ recogdb.dicFields['correctedPosB'] ]
        newDistA = read_data[ recogdb.dicFields['distA'] ]
        newDistB = read_data[ recogdb.dicFields['distB'] ]
        newDistAB = read_data[ recogdb.dicFields['distAB'] ]
        
        # Action identifier
        keyundofile.write( dicUndo[INVERTION] )
        
        # Modified fields
        keyundofile.write( '\t%s\t%c\t%c\n'%('svm', oldSVM, newSVM) )
        keyundofile.write( '\t%s\t%d\t%d\n'%('presentFish', oldFish, newFish) )
        keyundofile.write( '\t%s\t%d\t%d\n'%('correctedPosA', oldCorrectedPosA, newCorrectedPosA) )
        keyundofile.write( '\t%s\t%d\t%d\n'%('correctedPosB', oldCorrectedPosB, newCorrectedPosB) )
        keyundofile.write( '\t%s\t%f\t%f\n'%('distA', oldDistA, newDistA) )
        keyundofile.write( '\t%s\t%f\t%f\n'%('distB', oldDistB, newDistB) )
        keyundofile.write( '\t%s\t%f\t%f\n'%('distAB', oldDistAB, newDistAB) )
        
        keyundofile.close()


class IPIWindow(QtGui.QDialog):
    RButSize = 30
    RUndoLabelSize = 100
    RUndoStep = 140

    def __init__(self, db, undoFilename, folder):
        QtGui.QWidget.__init__(self)
        self.uiObject = Ui_IPIClick()
        self.uiObject.setupUi(self)
        
        self.modify = ModifySelector(db, undoFilename, folder)

        QtCore.QObject.connect(self.uiObject.okButton, QtCore.SIGNAL('clicked()'), self.okClicked)
        QtCore.QObject.connect(self.uiObject.cancelButton, QtCore.SIGNAL('clicked()'), self.close)
        
        self.replot=False

        self.move(0,0)

        self.options = []
        
        self.undoOptions = []

    def okClicked(self):
        for n,opt in enumerate(self.options):
            if opt.isChecked() == True:
                option = n
        
        if self.windowType == 'continuity':
            # Invert fish
            if option == 0:
                self.modify.invertIPI(self.off)
                self.replot = True
            # Convert to overlap
            elif option == 1:
                pass
            # Create SVM Pair
            elif option == 2:
                pass
            
        elif self.windowType == 'overlap':
            # Convert to single A
            if option == 0:
                pass
            # Convert to single B
            elif option == 1:
                pass
            
        elif self.windowType == 'single':
            # Invert SVM
            if option == 0:
                pass
            # Remove SVM
            elif option == 1:
                pass
            # Reapply continuity (recog iterate_from)
            elif option == 2:
                pass
        
        self.close()
    
    def createMainOptions(self,text):
        self.uiObject.mainOptionsBox = QtGui.QGroupBox(self.uiObject.gridLayoutWidget)
        self.uiObject.mainOptionsBox.setObjectName(_fromUtf8("MainOptionsBox"))
        self.uiObject.mainOptionsLayout.addWidget(self.uiObject.mainOptionsBox, 0, 0, 1, 1)
        self.uiObject.mainOptionsBox.deleteLater()
        self.setGroupBoxTitle(text)

    def fillTextBoxes(self, Parameters):
        self.off = Parameters[2]
        
        parText = self.generateParameterText(Parameters)
        self.setParameterText(parText)
        self.createMainOptions('Options: ')
        self.fillMainOptions(Parameters)
        
        modList = self.modify.parseModifications(self.off)
        if modList is not None:
            self.fillUndoOptions(modList)

    def fillUndoOptions(self, modList):
        self.undoOptions = []
        i = 0
        for action, dicActions in modList:
            RadioBut =  QtGui.QRadioButton(self.uiObject.scrollAreaWidgetContents)
            RadioBut.setObjectName(_fromUtf8('undo' + str(i)))
            RadioBut.setMinimumHeight(self.RButSize)
            self.uiObject.verticalLayout.addWidget(RadioBut)
            
            Label = QtGui.QLabel(self.uiObject.scrollAreaWidgetContents)
            Label.setObjectName(_fromUtf8('undolabel' + str(i)))
            Label.setMinimumHeight(self.RUndoLabelSize)
            self.uiObject.verticalLayout.addWidget(Label)
            
            font = QtGui.QFont()
            font.setFamily(_fromUtf8('Arial'))
            font.setPointSize(8)
            Label.setFont(font)
            
            self.undoOptions.append( (RadioBut, Label) )
            
            LabelText = ''
            for k in dicActions.iterkeys():
                LabelText = LabelText + k + ': ' + str(dicActions[k][0]) + ' -> ' + str(dicActions[k][1]) + '\n'
            
            self.setUndoOpt(i, action.strip(), LabelText)
            
            i = i + 1

    def fillMainOptions(self, Parameters):

        self.svm = Parameters[4]

        self.options = []

        # single continuity spike
        if self.svm != 's':
            if self.fish != 3:
                self.windowType = 'continuity'
                self.setMainText('Continuity spike selected')

                for i in xrange(3):
                    self.options.append( QtGui.QRadioButton(self.uiObject.mainOptionsBox) )
                    self.options[-1].setGeometry(QtCore.QRect(0, self.RButSize*(1+i), 300, self.RButSize))
                    self.options[-1].setObjectName(_fromUtf8('opt' + str(i)))

                self.setOpt(0, 'Invert fish classification')
                self.setOpt(1, 'Convert to overlapping spike')
                self.setOpt(2, 'Create SVM Pair')

            # Overlapping spike
            else:
                self.windowType = 'overlap'
                self.setMainText('Overlapping spikes selected')

                for i in xrange(2):
                    self.options.append( QtGui.QRadioButton(self.uiObject.mainOptionsBox) )
                    self.options[-1].setGeometry(QtCore.QRect(0, self.RButSize*(1+i), 300, self.RButSize))
                    self.options[-1].setObjectName(_fromUtf8('opt' + str(i)))

                self.setOpt(0, 'Convert to single A spike')
                self.setOpt(1, 'Convert to single B spike')

        # SVM spike
        else:
            self.windowType = 'svm'
            self.setMainText('SVM spike selected')

            for i in xrange(3):
                self.options.append( QtGui.QRadioButton(self.uiObject.mainOptionsBox) )
                self.options[-1].setGeometry(QtCore.QRect(0, self.RButSize*(1+i), 300, self.RButSize))
                self.options[-1].setObjectName(_fromUtf8('opt' + str(i)))

            self.setOpt(0, 'Invert SVM classification')
            self.setOpt(1, 'Remove SVM classification')
            self.setOpt(2, 'Recalculate continuity from this SVM')

    def parseSVMFlag(self,svmFlag):
        if svmFlag == 'a':
            return 'Spike has to much samples'
        elif svmFlag == 'd':
            return 'Interval between spikes (any fish) is too long'
        elif svmFlag == 'm':
            return 'Manually modificated'
        elif svmFlag == 'i':
            return 'Insufficient good channels'
        elif svmFlag == 'o':
            return 'Overlapping spikes'
        elif svmFlag == 'p':
            return 'Probability below minimum'
        elif svmFlag == 'w':
            return 'No pair detected'
        elif svmFlag == 's':
            return 'SVM Classified'
        elif svmFlag == 'c':
            return 'Previous spike was not ready for SVM classification'

    def generateParameterText(self,Par):
        self.fish = Par[0]
        if self.fish == 1:
            fishtxt = 'Fish A'
        elif self.fish == 2:
            fishtxt = 'Fish B'
        elif self.fish == 3:
            fishtxt = 'Both A + B'
        text = '' + \
            'fish: ' + '\n' + \
            str(fishtxt) + '\n\n' + \
            'Timestamp: ' + '\n' + \
            str(Par[1]) + '\n\n' + \
            'offset on .memmapf32 file (bytes): ' + '\n' + \
            str(Par[2]) + '\n\n' + \
            'direction: ' + '\n' + \
            str(Par[3]) + '\n\n' + \
            'SVM status: ' + '\n' + \
            str(self.parseSVMFlag(Par[4])) + '\n\n' + \
            'Probability for A: ' + '\n' + \
            str(Par[5]) + '\n\n' + \
            'Probability for B: ' + '\n' + \
            str(Par[6]) + '\n\n' + \
            'Euclidean distance from last single A: ' + '\n' + \
            str(Par[7]) + '\n\n' + \
            'Euclidean distance from last single B: ' + '\n' + \
            str(Par[8]) + '\n\n' + \
            'Euclidean distance from overlapping last single A and last single B: ' + '\n' + \
            str(Par[9]) + '\n\n'
        return text

    def setMainText(self, text):
        self.uiObject.mainText.setText(_translate("IPIClick", text, None))

    def setParameterText(self, text):
        self.uiObject.parameters.setText(_translate("IPIClick", text, None))

    def setGroupBoxTitle(self, text):
        self.uiObject.mainOptionsBox.setTitle(_translate("IPIClick", text, None))

    def setOpt(self, num, text):
        self.options[num].setText(_translate("IPIClick", text, None))

    def setUndoOpt(self,num, textRadio, textLabel):
        self.undoOptions[num][0].setText(_translate("IPIClick", textRadio, None))
        self.undoOptions[num][1].setText(_translate("IPIClick", textLabel, None))