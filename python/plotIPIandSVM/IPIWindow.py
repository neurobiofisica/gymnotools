from PyQt4 import QtCore, QtGui
from IPIClick_interface import *

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



class IPIWindow(QtGui.QDialog):
    RButSize = 30

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.uiObject = Ui_IPIClick()
        self.uiObject.setupUi(self)

        QtCore.QObject.connect(self.uiObject.okButton, QtCore.SIGNAL('clicked()'), self.okClicked)
        QtCore.QObject.connect(self.uiObject.cancelButton, QtCore.SIGNAL('clicked()'), self.close)

        self.move(0,0)

        self.options = []

    def okClicked(self):
        for n,opt in enumerate(self.options):
            if opt.isChecked() == True:
                print (self.svm,n)

    def createGroupBox(self,text):
        self.uiObject.groupBox = QtGui.QGroupBox(self.uiObject.gridLayoutWidget)
        self.uiObject.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.uiObject.gridLayout.addWidget(self.uiObject.groupBox, 0, 0, 1, 1)
        self.uiObject.groupBox.deleteLater()
        self.setGroupBoxTitle(text)

    def fillTextBoxes(self, Parameters):
        parText = self.generateParameterText(Parameters)
        self.setParameterText(parText)
        self.createGroupBox('Options: ')

        for i in self.options:
            try:
                del i
            except:
                pass

        self.svm = Parameters[4]

        self.options = []

        # single continuity spike
        if self.svm != 's':
            if self.fish != 3:
                self.setMainText('Continuity spike selected')

                for i in xrange(3):
                    self.options.append( QtGui.QRadioButton(self.uiObject.groupBox) )
                    self.options[-1].setGeometry(QtCore.QRect(0, self.RButSize*(1+i), 300, self.RButSize))
                    self.options[-1].setObjectName(_fromUtf8('opt' + str(i)))

                self.setOpt(0, 'Invert fish classification')
                self.setOpt(1, 'Convert to overlapping spike')
                self.setOpt(2, 'Create SVM Pair')

            # Overlapping spike
            else:
                self.setMainText('Overlapping spikes selected')

                for i in xrange(2):
                    self.options.append( QtGui.QRadioButton(self.uiObject.groupBox) )
                    self.options[-1].setGeometry(QtCore.QRect(0, self.RButSize*(1+i), 300, self.RButSize))
                    self.options[-1].setObjectName(_fromUtf8('opt' + str(i)))

                self.setOpt(0, 'Convert to single A spike')
                self.setOpt(1, 'Convert to single B spike')

        # SVM spike
        else:
            self.setMainText('SVM spike selected')

            for i in xrange(3):
                self.options.append( QtGui.QRadioButton(self.uiObject.groupBox) )
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
        self.uiObject.groupBox.setTitle(_translate("IPIClick", text, None))

    def setOpt(self, num, text):
        self.options[num].setText(_translate("IPIClick", text, None))
