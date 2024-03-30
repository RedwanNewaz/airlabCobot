from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QMainWindow
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6 import uic
from PyQt6.QtCore import QTimer
import configparser

from queue import Queue
import time
import numpy as np
import py_trees
from calibration import Calibrator, ReadTableData, WriteCalibration, LoadTable, WriteTable
from PickAndDrop import GridWorld, ControlInput, get_pnd_subtree, Robot
from PoseEstimator import NodeManager
from collections import namedtuple
class MainWindow(QMainWindow):
    def __init__(self, fig, ax, config):
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
        self.trackerPose = Queue()
        self.objNames = set()

        self.timer = QTimer()
        self.timer.timeout.connect(self.showTime)
        self.timer.start(100)

        # design Bt
        readTable = ReadTableData(self.tableWidget, self.checkBox.isChecked)
        self.writeTable = WriteTable(self.tableWidget, self.input, self.calibrationText)
        self.loadTable = LoadTable(self.tableWidget)
        self.calib = Calibrator(ax, self.canvas, readTable, self.calibrationText)
        self.writer = WriteCalibration(readTable, self.calibrationText)

        # calibration bt
        sel_calibrator = py_trees.composites.Selector(name="sel_calibrator", memory=True)
        sel_calibrator.add_children([self.calib, self.writer])

        sel_table = py_trees.composites.Selector(name="sel_table", memory=True)
        sel_table.add_children([readTable, self.writeTable])

        seq_calibrator = py_trees.composites.Sequence(name="seq_calibrator", memory=True)
        seq_calibrator.add_children([sel_table, sel_calibrator])

        self.root_calibration = py_trees.composites.Selector("RootSelector", True)
        self.root_calibration.add_children([self.loadTable, seq_calibrator])

        # pick and drop bt

        self.robot = Robot(config)
        self.actionReset.triggered.connect(self.robot.reset)
        self.actionDock.triggered.connect(self.robot.dock)
        self.pickButton.clicked.connect(self.robot.pick)
        self.dropButton.clicked.connect(self.robot.drop)
        self.terminated = False



        grid_world = GridWorld(config["GRID"])
        self.taskStatus = False
        self.controller = ControlInput(ax, self.canvas, grid_world)
        self.root_pnd = py_trees.composites.Selector("RootPickNDrop", True)
        sim_pnd = py_trees.composites.Sequence("sim_pnd", True)

        robotTree = get_pnd_subtree(self.robot, grid_world)
        sim_pnd.add_children([self.controller, robotTree])
        self.root_pnd.add_children([grid_world, sim_pnd])
        self.Event = namedtuple("event", "xdata ydata inaxes")
        self.__eventStart = time.time()
    def closeEvent(self, event):
        # do stuff
        print('[+] closeEvent()')
        self.terminated = True

    def onLoadCalibrationActionClick(self):
        self.loadTable.clicked = True
        self.root_calibration.tick_once()

    def onCalibrateButtonClicked(self):
        self.calib.clicked = True
        self.writer.clicked = False
        self.root_calibration.tick_once()


    def onWriteButtonClicked(self):
        self.calib.clicked = False
        self.writer.clicked = True
        self.writeTable.clicked = True
        self.root_calibration.tick_once()
    def showTime(self):
        while not self.trackerPose.empty():
            pose = self.trackerPose.get()

            elspased = time.time() - self.__eventStart
            if elspased > 20:
                event = self.Event(xdata=pose[0], ydata=pose[1], inaxes=True)
                self.controller.onclick(event)
                self.__eventStart = time.time()

                print('[+] trackerPose:', pose)
        self.root_pnd.tick_once()

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




if __name__ == '__main__':
    fig = Figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    # ax1, ax2 = fig.add_subplot(1, 2)


    ax1.axis('off')
    ax2.axis('off')

    fig.tight_layout()

    config = configparser.ConfigParser()
    config.read('config.ini')

    app = QApplication(sys.argv)
    window = MainWindow(fig, ax2, config)

    # start realsense thread
    model_path = config['YOLO']['model_path']
    poseNode = NodeManager(ax1, window, model_path, config)
    poseNode.start()

    window.show()
    sys.exit(app.exec())