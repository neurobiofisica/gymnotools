# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'IPIClick_interface.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IPIClick(object):
    def setupUi(self, IPIClick):
        IPIClick.setObjectName("IPIClick")
        IPIClick.resize(1228, 400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(IPIClick.sizePolicy().hasHeightForWidth())
        IPIClick.setSizePolicy(sizePolicy)
        IPIClick.setMinimumSize(QtCore.QSize(803, 400))
        IPIClick.setMaximumSize(QtCore.QSize(16777215, 400))
        self.mainText = QtWidgets.QLabel(IPIClick)
        self.mainText.setGeometry(QtCore.QRect(10, 10, 291, 51))
        self.mainText.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.mainText.setObjectName("mainText")
        self.parameters = QtWidgets.QLabel(IPIClick)
        self.parameters.setGeometry(QtCore.QRect(320, 10, 470, 380))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        self.parameters.setFont(font)
        self.parameters.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.parameters.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.parameters.setObjectName("parameters")
        self.gridLayoutWidget = QtWidgets.QWidget(IPIClick)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 70, 291, 291))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.mainOptionsLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.mainOptionsLayout.setContentsMargins(0, 0, 0, 0)
        self.mainOptionsLayout.setObjectName("mainOptionsLayout")
        self.layoutWidget = QtWidgets.QWidget(IPIClick)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 360, 291, 29))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.okButton = QtWidgets.QPushButton(self.layoutWidget)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(self.layoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.modificationsLabel = QtWidgets.QLabel(IPIClick)
        self.modificationsLabel.setGeometry(QtCore.QRect(800, 10, 121, 16))
        self.modificationsLabel.setObjectName("modificationsLabel")
        self.undoButton = QtWidgets.QPushButton(IPIClick)
        self.undoButton.setGeometry(QtCore.QRect(1080, 360, 141, 27))
        self.undoButton.setObjectName("undoButton")
        self.scrollArea = QtWidgets.QScrollArea(IPIClick)
        self.scrollArea.setGeometry(QtCore.QRect(800, 30, 421, 321))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 417, 317))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.retranslateUi(IPIClick)
        QtCore.QMetaObject.connectSlotsByName(IPIClick)

    def retranslateUi(self, IPIClick):
        _translate = QtCore.QCoreApplication.translate
        IPIClick.setWindowTitle(_translate("IPIClick", "spike info"))
        self.mainText.setText(_translate("IPIClick", "TextLabel"))
        self.parameters.setText(_translate("IPIClick", "TextLabel"))
        self.okButton.setText(_translate("IPIClick", "Ok"))
        self.cancelButton.setText(_translate("IPIClick", "Cancel"))
        self.modificationsLabel.setText(_translate("IPIClick", "Last Modifications:"))
        self.undoButton.setText(_translate("IPIClick", "Undo"))

