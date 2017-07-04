from PyQt5 import QtWidgets, QtCore
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure

class CanvasROC(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('False positive rate')
        self.ax.set_ylabel('True positive rate')
        self.ax.set_title('ROC Curve')

        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class ROCWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.canvas = CanvasROC()

        self.vbl = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbl)
        self.vbl.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.vbl.addWidget(self.toolbar)

        self.canvas.fig.subplots_adjust(bottom=0.18)
