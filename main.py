from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QMainWindow
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6 import uic
from PyQt6.QtCore import QTimer
from pymycobot.mycobot import MyCobot
from BT import NodeManager
from queue import Queue
import time



class MainWindow(QMainWindow):
    def __init__(self, fig):
        super().__init__()
        uic.loadUi('cobot3.ui', self)
        self.setWindowTitle("AiR L@b Cobot")


        self.setLayout(self.viewer)

        self.canvas = FigureCanvasQTAgg(fig)
        self.viewer.addWidget(self.canvas)

        toolbar = NavigationToolbar2QT(self.canvas, self)
        self.viewer.addWidget(toolbar)

        self.moveButton.clicked.connect(self.onMoveButtonClicked)
        self.resetButton.clicked.connect(self.onResetButtonClicked)
        self.writeButton.clicked.connect(self.onWriteButtonClicked)
        self.dockingButton.clicked.connect(self.onDockButtonClicked)

        self.mycobot = MyCobot('/dev/ttyACM0')
        self.calibrationLine = Queue()
        self.objNames = set()

        self.timer = QTimer()
        self.timer.timeout.connect(self.showTime)
        self.timer.start(100)

    def showTime(self):
        # update calibration box
        if self.checkBox.isChecked():
            while not self.calibrationLine.empty():
                text = self.calibrationLine.get()
                self.calibrationText.setPlainText(text)

    def onWriteButtonClicked(self):
        text = self.calibrationText.toPlainText().strip()
        with open('calibration/calibrations.txt', 'a+') as f:
            f.write(text + "\n")

    def onResetButtonClicked(self):
        angles = [0, 0, 0, 0, 0, 0]
        print('[+] resetting cobot')
        self.mycobot.send_angles(angles, 70)

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

    def onDockButtonClicked(self):
        reset = [153.19, 137.81, -153.54, 156.79, 87.27, 13.62]
        print("::set_free_mode()\n")
        self.mycobot.send_angles(reset, 100)
        time.sleep(5)
        self.mycobot.release_all_servos()
        print("docking success ...\n")



    def move(self, coords):
        # coords = [200.0, 200.0, 110.0, 0.0, -180.0, 2.51]
        coords = [coords[0], coords[1], 110.0, 0.0, -180.0, 2.51]
        self.mycobot.send_coords(coords, 70, 2)
        print("::send_coords() ==> send coords {}, speed 70, mode 0\n".format(coords))
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
    ax = fig.add_subplot()
    ax.axis('off')
    fig.tight_layout()

    app = QApplication(sys.argv)
    window = MainWindow(fig)
    model_path = "/home/airlab/Downloads/yolov8_realsense/yolov8_rs/yolov8m.pt"
    sense = NodeManager(ax, window, model_path)
    sense.start()

    window.show()
    sys.exit(app.exec())
    sense.terminate = True