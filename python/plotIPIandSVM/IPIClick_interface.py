# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'IPIClick_interface.ui'
#
# Created: Sat Mar 28 17:15:05 2015
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_IPIClick(object):
    def setupUi(self, IPIClick):
        IPIClick.setObjectName(_fromUtf8("IPIClick"))
        IPIClick.resize(831, 338)
        self.mainText = QtGui.QLabel(IPIClick)
        self.mainText.setGeometry(QtCore.QRect(10, 10, 741, 51))
        self.mainText.setObjectName(_fromUtf8("mainText"))
        self.parameters = QtGui.QLabel(IPIClick)
        self.parameters.setGeometry(QtCore.QRect(10, 70, 741, 51))
        self.parameters.setObjectName(_fromUtf8("parameters"))
        self.groupBox = QtGui.QGroupBox(IPIClick)
        self.groupBox.setGeometry(QtCore.QRect(140, 150, 120, 161))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.opt1 = QtGui.QRadioButton(self.groupBox)
        self.opt1.setGeometry(QtCore.QRect(0, 20, 105, 20))
        self.opt1.setObjectName(_fromUtf8("opt1"))
        self.opt2 = QtGui.QRadioButton(self.groupBox)
        self.opt2.setGeometry(QtCore.QRect(0, 40, 105, 20))
        self.opt2.setObjectName(_fromUtf8("opt2"))
        self.opt3 = QtGui.QRadioButton(self.groupBox)
        self.opt3.setGeometry(QtCore.QRect(0, 60, 105, 20))
        self.opt3.setObjectName(_fromUtf8("opt3"))

        self.retranslateUi(IPIClick)
        QtCore.QMetaObject.connectSlotsByName(IPIClick)

    def retranslateUi(self, IPIClick):
        IPIClick.setWindowTitle(_translate("IPIClick", "Form", None))
        self.mainText.setText(_translate("IPIClick", "TextLabel", None))
        self.parameters.setText(_translate("IPIClick", "TextLabel", None))
        self.groupBox.setTitle(_translate("IPIClick", "GroupBox", None))
        self.opt1.setText(_translate("IPIClick", "RadioButton", None))
        self.opt2.setText(_translate("IPIClick", "RadioButton", None))
        self.opt3.setText(_translate("IPIClick", "RadioButton", None))

