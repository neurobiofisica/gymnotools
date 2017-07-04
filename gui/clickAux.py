from PyQt5 import QtWidgets, QtCore
#from PyQt5.QtCore import SIGNAL

class ClickQLabel(QtWidgets.QLabel):

    clicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)
        
    def mouseReleaseEvent(self, ev):
        #self.emit(SIGNAL('clicked()'))
        self.clicked.emit(ev.globalPos())

class ClickQLineEdit(QtWidgets.QLineEdit):

    clicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)

    def mouseReleaseEvent(self, ev):
        #self.emit(SIGNAL('clicked()'))
        self.clicked.emit(ev.globalPos())
