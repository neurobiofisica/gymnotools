# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'graphicalInterface.ui'
#
# Created: Sat Mar 28 13:38:16 2015
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(1200, 900)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.formLayoutWidget = QtGui.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(0, 7, 1201, 891))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.formLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.graphIPI = graphIPI(self.formLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphIPI.sizePolicy().hasHeightForWidth())
        self.graphIPI.setSizePolicy(sizePolicy)
        self.graphIPI.setMaximumSize(QtCore.QSize(16777215, 350))
        self.graphIPI.setObjectName(_fromUtf8("graphIPI"))
        self.verticalLayout.addWidget(self.graphIPI)
        self.graphwave = graphwave(self.formLayoutWidget)
        self.graphwave.setObjectName(_fromUtf8("graphwave"))
        self.verticalLayout.addWidget(self.graphwave)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "IPI and SVM tool", None))

from .graphAux import graphIPI, graphwave
