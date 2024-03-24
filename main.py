from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QMainWindow
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6 import uic
from PyQt6.QtCore import QTimer
import operator

from queue import Queue
import time
import numpy as np
import py_trees
from calibration import Calibrator, ReadTableData, WriteCalibration, LoadTable

class MainWindow(QMainWindow):
    def __init__(self, fig, ax):
        super().__init__()
        uic.loadUi('cobot33.ui', self)
        self.setWindowTitle("AiR L@b Cobot")
        self.ax = ax

        # self.setLayout(self.viewer)

        self.canvas = FigureCanvasQTAgg(fig)
        self.viewer.addWidget(self.canvas)

        toolbar = NavigationToolbar2QT(self.canvas, self)
        self.viewer.addWidget(toolbar)

        # self.moveButton.clicked.connect(self.onMoveButtonClicked)
        # self.resetButton.clicked.connect(self.onResetButtonClicked)
        self.writeButton.clicked.connect(self.onWriteButtonClicked)
        self.calibrateButton.clicked.connect(self.onCalibrateButtonClicked)
        # self.dockingButton.clicked.connect(self.onDockButtonClicked)
        self.actionload_calibration.triggered.connect(self.onLoadCalibrationActionClick)


        self.calibrationLine = Queue()
        self.objNames = set()

        self.timer = QTimer()
        self.timer.timeout.connect(self.showTime)
        self.timer.start(100)

        # design Bt
        readTable = ReadTableData(self.tableWidget, self.checkBox.isChecked)
        self.loadTable = LoadTable(self.tableWidget)
        self.calib = Calibrator(ax, self.canvas, readTable, self.calibrationText)
        self.writer = WriteCalibration(readTable, self.calibrationText)


        sel_calibrator = py_trees.composites.Selector(name="sel_calibrator", memory=True)
        sel_calibrator.add_children([self.calib, self.writer])

        seq_calibrator = py_trees.composites.Sequence(name="seq_calibrator", memory=True)
        seq_calibrator.add_children([readTable, sel_calibrator])

        self.root = py_trees.composites.Selector("RootSelector", True)
        self.root.add_children([self.loadTable, seq_calibrator])


    def onLoadCalibrationActionClick(self):
        self.loadTable.clicked = True
        self.root.tick_once()

    def onCalibrateButtonClicked(self):
        self.calib.clicked = True
        self.writer.clicked = False
        self.root.tick_once()


    def onWriteButtonClicked(self):
        self.calib.clicked = False
        self.writer.clicked = True
        self.root.tick_once()
    def showTime(self):
        pass




if __name__ == '__main__':
    fig = Figure()
    ax = fig.add_subplot()
    ax.axis('off')
    fig.tight_layout()

    app = QApplication(sys.argv)
    window = MainWindow(fig, ax)
    window.show()
    sys.exit(app.exec())