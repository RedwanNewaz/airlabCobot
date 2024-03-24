from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QMainWindow
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6 import uic
from PyQt6.QtCore import QTimer
from scipy.optimize import least_squares

from queue import Queue
import time
import numpy as np

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

    def onLoadCalibrationActionClick(self):
        print('load action calibration triggered')
        rawData = np.loadtxt(f'calibration.csv', delimiter=',').astype('str')
        cobot_data = [",".join(r) for r in rawData[:, :2]]
        realsense_data = [",".join(r) for r in rawData[:, 2:]]
        combo = list(zip(cobot_data, realsense_data))
        header = ['cobot', 'realsense']
        self.populate_table(combo, header)

    def point_transformation(self, point, origin):
        x = (point - origin)
        x[1] *= -1
        return x

    def computeOptimalTransformation(self, camera, cobot):

        def calibrate(x0_param, xx, y):
            y_hat = np.array([self.point_transformation(x, x0_param) for x in xx])
            return np.linalg.norm(y_hat - y)

        def find_transformation(camera, cobot):
            # initial guess on the parameters
            x0 = np.array([0.0, 0.0])
            res_lsq = least_squares(calibrate, x0, args=(camera, cobot))

            print(
                f"x = {res_lsq.x[0]:.3f}, y = {res_lsq.x[1]:.3f}"
            )
            return np.array([res_lsq.x[0], res_lsq.x[1]])

        return find_transformation(camera, cobot)
    def onCalibrateButtonClicked(self):
        rowCount = self.tableWidget.rowCount()
        columnCount = self.tableWidget.columnCount()

        # read table widget
        calibrationData = [[[]] * columnCount for _ in range(rowCount)]
        for row in range(rowCount):
            for column in range(columnCount):
                item = self.tableWidget.item(row, column)
                data = list(map(float, item.text().split(',')))
                # print(row, column, data)
                # where data = [x, y]
                calibrationData[row][column] = data

        # seprate data files
        calibrationData = np.array(calibrationData).T
        cobot = np.column_stack((calibrationData[0][0], calibrationData[1][0]))
        realsense = np.column_stack((calibrationData[0][1], calibrationData[1][1]))
        # print('cobot', cobot)
        # print('realsense', realsense)

        # compute optimal transformation
        origin = self.computeOptimalTransformation(realsense, cobot)

        transformedData = realsense.copy()
        for i, p in enumerate(transformedData):
            transformedData[i] = self.point_transformation(p, origin)

        # show it to text box
        msg = f"x = {origin[0]:.3f}, y = {origin[1]:.3f}"
        self.calibrationText.setPlainText(msg)

        # plot them
        self.ax.fill(cobot[:, 0], cobot[:, 1], 'y', alpha=0.4)
        self.ax.fill(realsense[:, 0], realsense[:, 1], 'b')
        self.ax.fill(transformedData[:, 0], transformedData[:, 1], 'r', alpha=0.4)

        self.ax.legend(['cobot', 'realsense', 'transformed'])
        self.canvas.draw()

        # save calibration data
        camCalibrationData = np.hstack((cobot, realsense))
        np.savetxt('calibration.csv', camCalibrationData, delimiter=',', fmt='%0.3f')


    def onWriteButtonClicked(self):
        # cobot_data = [
        #     "-50, -280",
        #     "-280, -50",
        #     "-50, 280",
        #     "160, 160",
        #     "160, -160",
        #     "160, 60"
        # ]
        # realsense_data = [
        #     "235.68, -80.27",
        #     "3.32, -301.09",
        #     "242.80, -645.36",
        #     "448.93, -541.56",
        #     "477.33, -192.80",
        #     "458.48, -423.85"
        # ]

        # rawData = np.loadtxt(f'calibration.csv', delimiter=',').astype('str')
        # cobot_data = [ ",".join(r) for r in rawData[:, :2]]
        # realsense_data = [ ",".join(r) for r in rawData[:, 2:]]
        # combo = list(zip(cobot_data, realsense_data))
        # header = ['cobot', 'realsense']
        # self.populate_table(combo, header)
        pass
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