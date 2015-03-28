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

