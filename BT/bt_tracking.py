import py_trees
import py_trees.console as console
import numpy as np
import cv2
from py_trees import common
from time import time


class TrackingCheckBox(py_trees.behaviour.Behaviour):
    def __init__(self, window):
        self.window = window
        super().__init__("TrackingCheckBox")

    def update(self) -> common.Status:
        return self.status.SUCCESS if self.window.trackingBox.isChecked() else self.status.FAILURE



class Tracking(py_trees.behaviour.Behaviour):
    def __init__(self, window):
        self.window = window
        self.start_time = time()
        super().__init__("Tracking")

    @staticmethod
    def check_realsense_coord():
        input_string = py_trees.display.unicode_blackboard(key_filter={"/PoseEstimator/state"})
        lines = input_string.strip().split('\n')
        for line in lines:
            if ":" in line or "state" in line or 'Data' in line:
                continue
            msg_parse = line.strip().split(',')
            yield msg_parse

    def update(self) -> common.Status:
        current_time = time()
        elapsed_time = current_time - self.start_time
        if elapsed_time > 2.0:
            self.start_time = current_time
        else:
            return self.status.RUNNING

        for msg in self.check_realsense_coord():
            line = ",".join(msg)
            if self.window.comboBox.currentText() in line:
                coords = list(map(float, msg[1:]))
                self.logger.info( "move to " + line)
                self.window.move(coords)

        return self.status.SUCCESS

