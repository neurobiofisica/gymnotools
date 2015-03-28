from PyQt4 import QtCore, QtGui
from IPIClick_interface import *

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)



class IPIWindow(QtGui.QDialog):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.uiObject = Ui_IPIClick()
        self.uiObject.setupUi(self)

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
        text = '' + \
            'fish: ' + '\n' + \
            str(Par[0]) + '\n\n' + \
            'Timestamp: ' + '\n' + \
            str(Par[1]) + '\n\n' + \
            'offset on .memmapf32 file (bytes): ' + '\n' + \
            str(Par[2]) + '\n\n' + \
            'direction: ' + '\n' + \
            str(Par[3]) + '\n\n' + \
            'SVM cause: ' + '\n' + \
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
        if num==1:
            self.uiObject.opt1.setText(_translate("IPIClick", text, None))
        if num==2:
            self.uiObject.opt2.setText(_translate("IPIClick", text, None))
        if num==3:
            self.uiObject.opt3.setText(_translate("IPIClick", text, None))

