# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'single2overlapInterface.ui'
#
# Created: Thu Apr 23 20:11:37 2015
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
        single2overlap.resize(1361, 549)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(single2overlap.sizePolicy().hasHeightForWidth())
        single2overlap.setSizePolicy(sizePolicy)
        self.horizontalLayoutWidget = QtGui.QWidget(single2overlap)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 40, 1361, 441))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.graphsLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.graphsLayout.setMargin(0)
        self.graphsLayout.setObjectName(_fromUtf8("graphsLayout"))
        self.prevLayout = QtGui.QVBoxLayout()
        self.prevLayout.setObjectName(_fromUtf8("prevLayout"))
        self.prev1 = singleSignal(self.horizontalLayoutWidget)
        self.prev1.setObjectName(_fromUtf8("prev1"))
        self.prevLayout.addWidget(self.prev1)
        self.prev2 = singleSignal(self.horizontalLayoutWidget)
        self.prev2.setObjectName(_fromUtf8("prev2"))
        self.prevLayout.addWidget(self.prev2)
        self.graphsLayout.addLayout(self.prevLayout)
        self.spikeLayout = QtGui.QVBoxLayout()
        self.spikeLayout.setObjectName(_fromUtf8("spikeLayout"))
        self.spike = singleSignal(self.horizontalLayoutWidget)
        self.spike.setObjectName(_fromUtf8("spike"))
        self.spikeLayout.addWidget(self.spike)
        self.graphsLayout.addLayout(self.spikeLayout)
        self.nextLayout = QtGui.QVBoxLayout()
        self.nextLayout.setObjectName(_fromUtf8("nextLayout"))
        self.next1 = singleSignal(self.horizontalLayoutWidget)
        self.next1.setObjectName(_fromUtf8("next1"))
        self.nextLayout.addWidget(self.next1)
        self.next2 = singleSignal(self.horizontalLayoutWidget)
        self.next2.setObjectName(_fromUtf8("next2"))
        self.nextLayout.addWidget(self.next2)
        self.graphsLayout.addLayout(self.nextLayout)
        self.horizontalLayoutWidget_2 = QtGui.QWidget(single2overlap)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(1030, 490, 321, 41))
        self.horizontalLayoutWidget_2.setObjectName(_fromUtf8("horizontalLayoutWidget_2"))
        self.buttonsLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.buttonsLayout.setMargin(0)
        self.buttonsLayout.setObjectName(_fromUtf8("buttonsLayout"))
        self.okButton = QtGui.QPushButton(self.horizontalLayoutWidget_2)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.buttonsLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton(self.horizontalLayoutWidget_2)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.buttonsLayout.addWidget(self.cancelButton)
        self.channelSelector = QtGui.QSlider(single2overlap)
        self.channelSelector.setGeometry(QtCore.QRect(100, 500, 911, 29))
        self.channelSelector.setOrientation(QtCore.Qt.Horizontal)
        self.channelSelector.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.channelSelector.setObjectName(_fromUtf8("channelSelector"))
        self.channelLabel = QtGui.QLabel(single2overlap)
        self.channelLabel.setGeometry(QtCore.QRect(10, 490, 70, 18))
        self.channelLabel.setObjectName(_fromUtf8("channelLabel"))
        self.channelNumber = QtGui.QLabel(single2overlap)
        self.channelNumber.setGeometry(QtCore.QRect(10, 520, 70, 18))
        self.channelNumber.setObjectName(_fromUtf8("channelNumber"))
        self.infoTitle = QtGui.QLabel(single2overlap)
        self.infoTitle.setGeometry(QtCore.QRect(10, 10, 581, 18))
        self.infoTitle.setObjectName(_fromUtf8("infoTitle"))
        self.fishSelector = QtGui.QGroupBox(single2overlap)
        self.fishSelector.setGeometry(QtCore.QRect(310, 10, 261, 31))
        self.fishSelector.setTitle(_fromUtf8(""))
        self.fishSelector.setObjectName(_fromUtf8("fishSelector"))
        self.widget = QtGui.QWidget(self.fishSelector)
        self.widget.setGeometry(QtCore.QRect(0, 0, 252, 25))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.fishSelectorLayout = QtGui.QHBoxLayout(self.widget)
        self.fishSelectorLayout.setMargin(0)
        self.fishSelectorLayout.setObjectName(_fromUtf8("fishSelectorLayout"))
        self.fishAButton = QtGui.QRadioButton(self.widget)
        self.fishAButton.setObjectName(_fromUtf8("fishAButton"))
        self.fishSelectorLayout.addWidget(self.fishAButton)
        self.fishBButton = QtGui.QRadioButton(self.widget)
        self.fishBButton.setObjectName(_fromUtf8("fishBButton"))
        self.fishSelectorLayout.addWidget(self.fishBButton)

        self.retranslateUi(single2overlap)
        QtCore.QMetaObject.connectSlotsByName(single2overlap)

    def retranslateUi(self, single2overlap):
        single2overlap.setWindowTitle(QtGui.QApplication.translate("single2overlap", "IPI and SVM tool", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("single2overlap", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("single2overlap", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.channelLabel.setText(QtGui.QApplication.translate("single2overlap", "Channel", None, QtGui.QApplication.UnicodeUTF8))
        self.channelNumber.setText(QtGui.QApplication.translate("single2overlap", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.infoTitle.setText(QtGui.QApplication.translate("single2overlap", "Select the instant of the spike for fish:", None, QtGui.QApplication.UnicodeUTF8))
        self.fishAButton.setText(QtGui.QApplication.translate("single2overlap", "Fish A", None, QtGui.QApplication.UnicodeUTF8))
        self.fishBButton.setText(QtGui.QApplication.translate("single2overlap", "Fish B", None, QtGui.QApplication.UnicodeUTF8))

from single2overlapAux import singleSignal
