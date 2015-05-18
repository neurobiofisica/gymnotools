from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL

class clickQLabel(QtGui.QLabel):

    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)
        
    def mouseReleaseEvent(self, ev):
        self.emit(SIGNAL('clicked()'))
