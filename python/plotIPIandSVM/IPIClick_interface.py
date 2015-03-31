# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'IPIClick_interface.ui'
#
# Created: Tue Mar 31 13:29:50 2015
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
        IPIClick.resize(803, 400)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(IPIClick.sizePolicy().hasHeightForWidth())
        IPIClick.setSizePolicy(sizePolicy)
        IPIClick.setMinimumSize(QtCore.QSize(803, 400))
        IPIClick.setMaximumSize(QtCore.QSize(803, 400))
        self.mainText = QtGui.QLabel(IPIClick)
        self.mainText.setGeometry(QtCore.QRect(10, 10, 291, 51))
        self.mainText.setObjectName(_fromUtf8("mainText"))
        self.parameters = QtGui.QLabel(IPIClick)
        self.parameters.setGeometry(QtCore.QRect(320, 10, 470, 380))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(8)
        self.parameters.setFont(font)
        self.parameters.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.parameters.setObjectName(_fromUtf8("parameters"))
        self.gridLayoutWidget = QtGui.QWidget(IPIClick)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 70, 291, 291))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.layoutWidget = QtGui.QWidget(IPIClick)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 360, 291, 29))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.okButton = QtGui.QPushButton(self.layoutWidget)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.horizontalLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton(self.layoutWidget)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout.addWidget(self.cancelButton)

        self.retranslateUi(IPIClick)
        QtCore.QMetaObject.connectSlotsByName(IPIClick)

    def retranslateUi(self, IPIClick):
        IPIClick.setWindowTitle(_translate("IPIClick", "spike info", None))
        self.mainText.setText(_translate("IPIClick", "TextLabel", None))
        self.parameters.setText(_translate("IPIClick", "TextLabel", None))
        self.okButton.setText(_translate("IPIClick", "Ok", None))
        self.cancelButton.setText(_translate("IPIClick", "Cancel", None))

