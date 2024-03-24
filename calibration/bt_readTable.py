import py_trees
import py_trees.console as console
import numpy as np
from py_trees import common
from scipy.optimize import least_squares
class ReadTableData(py_trees.behaviour.Behaviour):
    def __init__(self, tableWidget):
        self.tableWidget = tableWidget
        super(ReadTableData, self).__init__('ReadTableData')

    def update(self) -> common.Status:
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

        # seperate data files
        calibrationData = np.array(calibrationData).T
        self.cobot = np.column_stack((calibrationData[0][0], calibrationData[1][0]))
        self.realsense = np.column_stack((calibrationData[0][1], calibrationData[1][1]))
        return self.status.SUCCESS