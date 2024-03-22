from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QMainWindow
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6 import uic
from pymycobot.mycobot import MyCobot
from BT import NodeManager

class MainWindow(QMainWindow):
    def __init__(self, fig):
        super().__init__()
        uic.loadUi('cobot.ui', self)

        self.setLayout(self.viewer)

        self.canvas = FigureCanvasQTAgg(fig)
        self.viewer.addWidget(self.canvas)

        toolbar = NavigationToolbar2QT(self.canvas, self)
        self.viewer.addWidget(toolbar)

        self.moveButton.clicked.connect(self.onMoveButtonClicked)
        self.resetButton.clicked.connect(self.onResetButtonClicked)

        self.mycobot = MyCobot('/dev/ttyACM1')

    def onResetButtonClicked(self):
        angles = [0, 0, 0, 0, 0, 0]
        print('[+] resetting cobot')
        self.mycobot.send_angles(angles, 70)

    def onMoveButtonClicked(self):

        # read from textbox
        inputText = self.input.text()

        cmd = list(map(float, inputText.strip().split(',')))
        if len(cmd) >= 2:
            print(f'[+] move to {cmd}')
            self.move(cmd)



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






if __name__ == '__main__':

    fig = Figure()
    ax = fig.add_subplot()
    ax.axis('off')
    fig.tight_layout()

    app = QApplication(sys.argv)
    window = MainWindow(fig)

    sense = NodeManager(ax, window)
    sense.start()

    window.show()
    sys.exit(app.exec())
    sense.terminate = True