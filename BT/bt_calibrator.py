import py_trees
import py_trees.console as console
import numpy as np
import cv2
from py_trees import common


class CalibratorCheckBox(py_trees.behaviour.Behaviour):
    def __init__(self, window):
        self.window = window
        super().__init__("CalibratorCheckBox")

    def update(self) -> common.Status:
        return self.status.SUCCESS if self.window.checkBox.isChecked() else self.status.FAILURE


class Calibrator(py_trees.behaviour.Behaviour):
    def __init__(self, window):
        self.window = window
        super().__init__("Calibrator")

    @staticmethod
    def check_realsense_coord():
        input_string = py_trees.display.unicode_blackboard(key_filter={"/PoseEstimator/state"})
        lines = input_string.strip().split('\n')
        for line in lines:
            if ":" in line or "state" in line or 'Data' in line:
                continue
            msg_parse = line.strip().split(',')
            yield msg_parse

    def update(self):
        for msg in self.check_realsense_coord():
            line = ",".join(msg)
            self.logger.info(line)
            if self.window.comboBox.currentText() in line:
                self.window.calibrationLine.put(line)

        return self.status.SUCCESS