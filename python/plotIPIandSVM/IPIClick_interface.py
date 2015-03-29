# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'IPIClick_interface.ui'
#
# Created: Sat Mar 28 22:43:19 2015
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
        IPIClick.resize(803, 498)
        self.mainText = QtGui.QLabel(IPIClick)
        self.mainText.setGeometry(QtCore.QRect(10, 10, 291, 51))
        self.mainText.setObjectName(_fromUtf8("mainText"))
        self.parameters = QtGui.QLabel(IPIClick)
        self.parameters.setGeometry(QtCore.QRect(320, 10, 471, 481))
        self.parameters.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.parameters.setObjectName(_fromUtf8("parameters"))
        self.gridLayoutWidget = QtGui.QWidget(IPIClick)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 70, 291, 371))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.widget = QtGui.QWidget(IPIClick)
        self.widget.setGeometry(QtCore.QRect(10, 450, 291, 29))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton_3 = QtGui.QPushButton(self.widget)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pushButton_2 = QtGui.QPushButton(self.widget)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.horizontalLayout.addWidget(self.pushButton_2)

        self.retranslateUi(IPIClick)
        QtCore.QMetaObject.connectSlotsByName(IPIClick)

    def retranslateUi(self, IPIClick):
        IPIClick.setWindowTitle(_translate("IPIClick", "spike info", None))
        self.mainText.setText(_translate("IPIClick", "TextLabel", None))
        self.parameters.setText(_translate("IPIClick", "TextLabel", None))
        self.pushButton_3.setText(_translate("IPIClick", "Ok", None))
        self.pushButton_2.setText(_translate("IPIClick", "Cancel", None))

