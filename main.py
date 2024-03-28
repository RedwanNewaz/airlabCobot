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
from calibration import Calibrator, ReadTableData, WriteCalibration, LoadTable, WriteTable
from PoseEstimator import NodeManager

from pymycobot import MyCobot
import configparser

class MainWindow(QMainWindow):
    def __init__(self, fig, ax, config):
        super().__init__()
        uic.loadUi('cobot33.ui', self)
        self.setWindowTitle("AiR L@b Cobot")
        self.ax = ax
        self.config = config

        self.canvas = FigureCanvasQTAgg(fig)
        self.viewer.addWidget(self.canvas)

        toolbar = NavigationToolbar2QT(self.canvas, self)
        self.viewer.addWidget(toolbar)


        self.writeButton.clicked.connect(self.onWriteButtonClicked)
        self.calibrateButton.clicked.connect(self.onCalibrateButtonClicked)
        self.actionload_calibration.triggered.connect(self.onLoadCalibrationActionClick)


        self.calibrationLine = Queue()
        self.objNames = set()

        self.timer = QTimer()
        self.timer.timeout.connect(self.showTime)
        self.timer.start(100)

        # design Bt
        readTable = ReadTableData(self.tableWidget, self.checkBox.isChecked)
        self.writeTable = WriteTable(self.tableWidget, self.input, self.calibrationText, self.getCobotCoords)
        self.loadTable = LoadTable(self.tableWidget)
        self.calib = Calibrator(ax, self.canvas, readTable, self.calibrationText)
        self.writer = WriteCalibration(readTable, self.calibrationText)


        sel_calibrator = py_trees.composites.Selector(name="sel_calibrator", memory=True)
        sel_calibrator.add_children([self.calib, self.writer])

        sel_table = py_trees.composites.Selector(name="sel_table", memory=True)
        sel_table.add_children([readTable, self.writeTable])

        seq_calibrator = py_trees.composites.Sequence(name="seq_calibrator", memory=True)
        seq_calibrator.add_children([sel_table, sel_calibrator])

        self.root = py_trees.composites.Selector("RootSelector", True)
        self.root.add_children([self.loadTable, seq_calibrator])


        # add cobot functionalities
        #TODO read port from config file
        port = self.config['COBOT']['port']

        self.mycobot = MyCobot(port, 115200)

        self.mycobot.set_pin_mode(2, 1)
        self.mycobot.set_pin_mode(5, 1)

        self.actionReset.triggered.connect(self.onResetButtonClicked)
        self.actionDock.triggered.connect(self.onDockButtonClicked)
        self.moveButton.clicked.connect(self.onMoveButtonClicked)
        self.pickButton.clicked.connect(self.onPickButtonClicked)
        self.dropButton.clicked.connect(self.onDropButtonClicked)
        self.terminated = False


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
        self.writeTable.clicked = True
        self.root.tick_once()
    def showTime(self):
        if self.checkBox.isChecked():
            while not self.calibrationLine.empty():
                text = self.calibrationLine.get()
                self.calibrationText.setPlainText(text)

    def onResetButtonClicked(self):
        angles = [0, 0, 0, 0, 0, 0]
        print('[+] resetting cobot')
        self.mycobot.send_angles(angles, 70)

    def onDockButtonClicked(self):
        reset = [153.19, 137.81, -153.54, 156.79, 87.27, 13.62]
        print("::set_free_mode()\n")
        self.mycobot.send_angles(reset, 100)
        time.sleep(float(self.config['COBOT']['sleep']))
        self.mycobot.release_all_servos()
        print("docking success ...\n")

    def move(self, coords):
        def sign(x):
            return -1.0 if x < 0 else 1.0
        if(len(coords) == 2):
            coords.append(float(self.config['COBOT']['altitude']))
        # coords = [200.0, 200.0, 110.0, 0.0, -180.0, 2.51]
        coords[0] = sign(coords[0]) * min(200.0, abs(coords[0]))
        coords[1] = sign(coords[1]) * min(200.0, abs(coords[1]))

        coords = [coords[0], coords[1], coords[2], 0.0, -180.0, 2.51]
        self.mycobot.send_coords(coords, 70, 2)
        print("::send_coords() ==> send coords {}, speed 70, mode 0\n".format(coords))

    def onMoveButtonClicked(self):
        # read from textbox
        inputText = self.input.text()
        if ',' not in inputText:
            print('[-] invalid input!')
            return

        cmd = list(map(float, inputText.strip().split(',')))
        if len(cmd) >= 2:
            print(f'[+] move to {cmd}')
            self.move(cmd)

    def getCobotCoords(self):
        coords = list(self.mycobot.get_coords())
        return f"{coords[0]},{coords[1]}"

    def onPickButtonClicked(self):
        #read this parameter from config file
        coords = list(self.mycobot.get_coords())
        print(f'current coord {coords}')
        val = float(self.config['COBOT']['down'])
        coords[2] -= val # lower down
        print(f'desire coord {coords}')
        self.move(coords)
        self.mycobot.set_basic_output(2, 0)
        self.mycobot.set_basic_output(5, 0)
        time.sleep(float(self.config['COBOT']['sleep']))
        coords[2] += val  # going back
        self.move(coords)

    def onDropButtonClicked(self):

        coords = list(self.mycobot.get_coords())
        print(f'current coord {coords}')
        val = 100
        coords[2] -= val  # lower down
        print(f'desire coord {coords}')
        self.move(coords)
        time.sleep(float(self.config['COBOT']['sleep']))
        self.mycobot.set_basic_output(2, 1)
        self.mycobot.set_basic_output(5, 1)
        coords[2] += val  # going back
        self.move(coords)

    def populate_table(self, data):
        # Set the table dimensions and headers
        self.tableWidget.setRowCount(len(data))  # Set number of rows
        self.tableWidget.setColumnCount(2)  # Set number of columns
        self.tableWidget.setHorizontalHeaderLabels(["Object", "Conf Score"])  # Set column headers

        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(str(cell))
                self.tableWidget.setItem(i, j, item)

                # update combo box
                if j == 0:
                    name = data[i][j]
                    if name not in self.objNames:
                        self.objNames.add(name)
                        self.comboBox.addItem(name)

    def closeEvent(self, event):
        # do stuff
        print('[+] closeEvent()')
        self.terminated = True




if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    fig = Figure()
    ax = fig.add_subplot()
    ax.axis('off')
    fig.tight_layout()

    app = QApplication(sys.argv)
    window = MainWindow(fig, ax, config)

    model_path = config['YOLO']['model_path']
    poseNode = NodeManager(ax, window, model_path, config)
    poseNode.start()


    window.show()
    sys.exit(app.exec())
    poseNode.terminate = True

