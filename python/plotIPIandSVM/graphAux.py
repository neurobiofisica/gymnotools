from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure

NChan=11
NColumns=2
NRows = NChan/NColumns + NChan%NColumns

class CanvasIPI(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class Canvaswave(FigureCanvas):
    def __init__(self):
        self.NColumns = NColumns

        self.fig = Figure()
        self.sigaxes = [self.fig.add_subplot(NRows,NColumns,1)] #2 columns
        self.sigaxes += [self.fig.add_subplot(NRows,NColumns,i, \
                sharex=self.sigaxes[0], sharey=self.sigaxes[0]) \
                for i in xrange(2,NChan+1)]

        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)

class graphIPI(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.canvas = CanvasIPI()
        self.vbl = QtGui.QVBoxLayout()
        self.setLayout(self.vbl)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

class graphwave(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.canvas = Canvaswave()
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
