import py_trees.console as console
import py_trees
from bt_cam import Camera
from bt_detector import Detector
from bt_pose_estimator import PoseEstimator
from threading import Thread
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QMainWindow
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6 import uic
from pymycobot.mycobot import MyCobot
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



class Sensor(Thread):
    def __init__(self, ax, window):
        Thread.__init__(self)
        cam = Camera(ax, window)
        model_path = "/home/airlab/Downloads/yolov8_realsense/yolov8_rs/yolov8m.pt"
        detector = Detector(cam, model_path)
        pose_estimator = PoseEstimator(cam, detector)


        seq_detector = py_trees.composites.Sequence(name="root", memory=True)
        seq_detector.add_children([detector, pose_estimator])


        root = py_trees.composites.Parallel(
            name="airlabCobot",
            # policy=py_trees.common.ParallelPolicy.SuccessOnAll()
            # policy=py_trees.common.ParallelPolicy.SuccessOnOne()
            policy=py_trees.common.ParallelPolicy.SuccessOnSelected([seq_detector])
        )
        root.add_children([cam, seq_detector])


        task = py_trees.composites.Sequence("Sequence", True)
        task.add_child(root)
        self.behaviour_tree = py_trees.trees.BehaviourTree(task)
        self.terminate = False

    def run(self):
        while not self.terminate:
            self.behaviour_tree.tick()




if __name__ == '__main__':

    fig = Figure()
    ax = fig.add_subplot()
    ax.axis('off')
    fig.tight_layout()

    app = QApplication(sys.argv)
    window = MainWindow(fig)

    sense = Sensor(ax, window)
    sense.start()

    window.show()
    sys.exit(app.exec())
    sense.terminate = True