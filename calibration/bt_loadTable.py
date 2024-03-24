import py_trees
import numpy as np
from PyQt6.QtWidgets import QTableWidgetItem
class LoadTable(py_trees.behaviour.Behaviour):
    def __init__(self, tableWidget):
        self.tableWidget = tableWidget
        self.clicked = False
        super(LoadTable, self).__init__("Load Table")

    def populate_table(self, data, header):
        # Set the table dimensions and headers
        self.tableWidget.setRowCount(len(data))  # Set number of rows
        self.tableWidget.setColumnCount(len(header))  # Set number of columns
        self.tableWidget.setHorizontalHeaderLabels(header)  # Set column headers

        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(str(cell))
                self.tableWidget.setItem(i, j, item)

    def update(self):
        if not self.clicked:
            return self.status.FAILURE

        rawData = np.loadtxt(f'calibration.csv', delimiter=',').astype('str')
        cobot_data = [",".join(r) for r in rawData[:, :2]]
        realsense_data = [",".join(r) for r in rawData[:, 2:]]
        combo = list(zip(cobot_data, realsense_data))
        header = ['cobot', 'realsense']
        self.populate_table(combo, header)
        self.clicked = False
        self.logger.info('load action calibration triggered')
        return self.status.SUCCESS
