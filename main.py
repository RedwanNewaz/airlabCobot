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
from calibration import Calibrator, ReadTableData, WriteCalibration

class MainWindow(QMainWindow):
    def __init__(self, fig, ax):
        super().__init__()
        uic.loadUi('cobot33.ui', self)
        self.setWindowTitle("AiR L@b Cobot")
        self.ax = ax

        self.setLayout(self.viewer)

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
        table = ReadTableData(self.tableWidget)
        self.calib = Calibrator(ax, self.canvas, table, self.calibrationText)
        self.writer = WriteCalibration(table, self.calibrationText)

        sel_calibrator = py_trees.composites.Selector(name="sel_calibrator", memory=True)
        sel_calibrator.add_children([self.calib, self.writer])


        seq_calibrator = py_trees.composites.Sequence(name="seq_calibrator", memory=True)
        seq_calibrator.add_children([table, sel_calibrator])

        self.root = py_trees.composites.Sequence("Sequence", True)
        self.root.add_children([seq_calibrator])

    def onLoadCalibrationActionClick(self):
        print('load action calibration triggered')
        rawData = np.loadtxt(f'calibration.csv', delimiter=',').astype('str')
        cobot_data = [",".join(r) for r in rawData[:, :2]]
        realsense_data = [",".join(r) for r in rawData[:, 2:]]
        combo = list(zip(cobot_data, realsense_data))
        header = ['cobot', 'realsense']
        self.populate_table(combo, header)



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

    def populate_table(self, data, header):
        # Set the table dimensions and headers
        self.tableWidget.setRowCount(len(data))  # Set number of rows
        self.tableWidget.setColumnCount(len(header))  # Set number of columns
        self.tableWidget.setHorizontalHeaderLabels(header)  # Set column headers

        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(str(cell))
                self.tableWidget.setItem(i, j, item)

                # # update combo box
                # if j == 0:
                #     name = data[i][j]
                #     if name not in self.objNames:
                #         self.objNames.add(name)
                #         self.comboBox.addItem(name)


if __name__ == '__main__':
    fig = Figure()
    ax = fig.add_subplot()
    ax.axis('off')
    fig.tight_layout()

    app = QApplication(sys.argv)
    window = MainWindow(fig, ax)
    window.show()
    sys.exit(app.exec())