# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'single2overlapInterface.ui'
#
# Created: Fri Apr 24 23:35:04 2015
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_single2overlap(object):
    def setupUi(self, single2overlap):
        single2overlap.setObjectName(_fromUtf8("single2overlap"))
        single2overlap.setWindowModality(QtCore.Qt.WindowModal)
        single2overlap.resize(1533, 803)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(single2overlap.sizePolicy().hasHeightForWidth())
        single2overlap.setSizePolicy(sizePolicy)
        single2overlap.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.gridLayout = QtGui.QGridLayout(single2overlap)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.mainLayout.setObjectName(_fromUtf8("mainLayout"))
        self.infoTitle = QtGui.QLabel(single2overlap)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.infoTitle.sizePolicy().hasHeightForWidth())
        self.infoTitle.setSizePolicy(sizePolicy)
        self.infoTitle.setObjectName(_fromUtf8("infoTitle"))
        self.mainLayout.addWidget(self.infoTitle, 0, 0, 1, 1)
        self.fishSelector = QtGui.QGroupBox(single2overlap)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.fishSelector.sizePolicy().hasHeightForWidth())
        self.fishSelector.setSizePolicy(sizePolicy)
        self.fishSelector.setTitle(_fromUtf8(""))
        self.fishSelector.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.fishSelector.setObjectName(_fromUtf8("fishSelector"))
        self.layoutWidget = QtGui.QWidget(self.fishSelector)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 252, 25))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.fishSelectorLayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.fishSelectorLayout.setMargin(0)
        self.fishSelectorLayout.setObjectName(_fromUtf8("fishSelectorLayout"))
        self.fishAButton = QtGui.QRadioButton(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fishAButton.sizePolicy().hasHeightForWidth())
        self.fishAButton.setSizePolicy(sizePolicy)
        self.fishAButton.setObjectName(_fromUtf8("fishAButton"))
        self.fishSelectorLayout.addWidget(self.fishAButton)
        self.fishBButton = QtGui.QRadioButton(self.layoutWidget)
        self.fishBButton.setObjectName(_fromUtf8("fishBButton"))
        self.fishSelectorLayout.addWidget(self.fishBButton)
        self.mainLayout.addWidget(self.fishSelector, 0, 1, 1, 1)
        self.graphsLayout = QtGui.QHBoxLayout()
        self.graphsLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.graphsLayout.setObjectName(_fromUtf8("graphsLayout"))
        self.prevLayout = QtGui.QVBoxLayout()
        self.prevLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.prevLayout.setObjectName(_fromUtf8("prevLayout"))
        self.prev1 = singleSignal(single2overlap)
        self.prev1.setObjectName(_fromUtf8("prev1"))
        self.prevLayout.addWidget(self.prev1)
        self.prev2 = singleSignal(single2overlap)
        self.prev2.setObjectName(_fromUtf8("prev2"))
        self.prevLayout.addWidget(self.prev2)
        self.graphsLayout.addLayout(self.prevLayout)
        self.spikeLayout = QtGui.QVBoxLayout()
        self.spikeLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.spikeLayout.setObjectName(_fromUtf8("spikeLayout"))
        self.spike = singleSignal(single2overlap)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.spike.sizePolicy().hasHeightForWidth())
        self.spike.setSizePolicy(sizePolicy)
        self.spike.setObjectName(_fromUtf8("spike"))
        self.spikeLayout.addWidget(self.spike)
        self.graphsLayout.addLayout(self.spikeLayout)
        self.nextLayout = QtGui.QVBoxLayout()
        self.nextLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.nextLayout.setObjectName(_fromUtf8("nextLayout"))
        self.next1 = singleSignal(single2overlap)
        self.next1.setObjectName(_fromUtf8("next1"))
        self.nextLayout.addWidget(self.next1)
        self.next2 = singleSignal(single2overlap)
        self.next2.setObjectName(_fromUtf8("next2"))
        self.nextLayout.addWidget(self.next2)
        self.graphsLayout.addLayout(self.nextLayout)
        self.mainLayout.addLayout(self.graphsLayout, 1, 0, 1, 3)
        self.bottomLayout = QtGui.QHBoxLayout()
        self.bottomLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.bottomLayout.setObjectName(_fromUtf8("bottomLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.verticalLayout.setContentsMargins(-1, 10, -1, 10)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.channelLabel = QtGui.QLabel(single2overlap)
        self.channelLabel.setObjectName(_fromUtf8("channelLabel"))
        self.verticalLayout.addWidget(self.channelLabel)
        self.channelNumber = QtGui.QLabel(single2overlap)
        self.channelNumber.setObjectName(_fromUtf8("channelNumber"))
        self.verticalLayout.addWidget(self.channelNumber)
        self.bottomLayout.addLayout(self.verticalLayout)
        self.channelSelector = QtGui.QSlider(single2overlap)
        self.channelSelector.setOrientation(QtCore.Qt.Horizontal)
        self.channelSelector.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.channelSelector.setObjectName(_fromUtf8("channelSelector"))
        self.bottomLayout.addWidget(self.channelSelector)
        self.buttonsLayout = QtGui.QHBoxLayout()
        self.buttonsLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.buttonsLayout.setObjectName(_fromUtf8("buttonsLayout"))
        self.okButton = QtGui.QPushButton(single2overlap)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.buttonsLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton(single2overlap)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.buttonsLayout.addWidget(self.cancelButton)
        self.bottomLayout.addLayout(self.buttonsLayout)
        self.mainLayout.addLayout(self.bottomLayout, 2, 0, 1, 3)
        self.mainLayout.setRowMinimumHeight(0, 40)
        self.mainLayout.setRowMinimumHeight(2, 80)
        self.mainLayout.setRowStretch(0, 1)
        self.mainLayout.setRowStretch(1, 20)
        self.mainLayout.setRowStretch(2, 1)
        self.gridLayout.addLayout(self.mainLayout, 0, 0, 1, 1)

        self.retranslateUi(single2overlap)
        QtCore.QMetaObject.connectSlotsByName(single2overlap)

    def retranslateUi(self, single2overlap):
        single2overlap.setWindowTitle(QtGui.QApplication.translate("single2overlap", "IPI and SVM tool", None, QtGui.QApplication.UnicodeUTF8))
        self.infoTitle.setText(QtGui.QApplication.translate("single2overlap", "Select the instant of the spike for fish:", None, QtGui.QApplication.UnicodeUTF8))
        self.fishAButton.setText(QtGui.QApplication.translate("single2overlap", "Fish A", None, QtGui.QApplication.UnicodeUTF8))
        self.fishBButton.setText(QtGui.QApplication.translate("single2overlap", "Fish B", None, QtGui.QApplication.UnicodeUTF8))
        self.channelLabel.setText(QtGui.QApplication.translate("single2overlap", "Channel", None, QtGui.QApplication.UnicodeUTF8))
        self.channelNumber.setText(QtGui.QApplication.translate("single2overlap", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("single2overlap", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("single2overlap", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

from single2overlapAux import singleSignal
