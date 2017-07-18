from PyQt5 import QtGui, QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure

import sys,os
if sys.version_info.major == 3:
    xrange = range

sys.path.append( os.path.abspath('..') )
from read_param import *
# import NChan, freq, winSize

NColumns=2
NRows = NChan/NColumns + NChan%NColumns

class CanvasIPI(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class Canvaswave(FigureCanvas):
    def __init__(self):
        self.NColumns = NColumns

        self.fig = Figure()
        self.sigaxes = [self.fig.add_subplot(NRows,NColumns,1)] #2 columns
        self.sigaxes += [self.fig.add_subplot(NRows,NColumns,i, \
                sharex=self.sigaxes[0]) \
                for i in xrange(2,NChan+1)]

        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

class graphIPI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.canvas = CanvasIPI()
        self.vbl = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbl)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

class graphwave(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.canvas = Canvaswave()
        self.vbl = QtWidgets.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
