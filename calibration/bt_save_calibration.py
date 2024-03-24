import py_trees
import numpy as np
import py_trees.console as console
from py_trees import common


class WriteCalibration(py_trees.behaviour.Behaviour):
    def __init__(self, table, msgbox):
        self.table = table
        self.msgbox = msgbox
        self.clicked = False
        super(WriteCalibration, self).__init__('WriteCalibration')

    def update(self):
        if not self.clicked:
            return self.status.FAILURE
        cobot, realsense = self.table.cobot, self.table.realsense
        # save calibration data
        camCalibrationData = np.hstack((cobot, realsense))
        np.savetxt('calibration.csv', camCalibrationData, delimiter=',', fmt='%0.3f')
        self.clicked = False

        # show debug message
        msg = f"[+] saved in calibration.csv"
        self.msgbox.setPlainText(msg)
        self.logger.info(msg)
        return self.status.SUCCESS

