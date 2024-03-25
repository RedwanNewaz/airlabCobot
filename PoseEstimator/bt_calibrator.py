import py_trees
import py_trees.console as console
import numpy as np
import cv2
from py_trees import common
import pyrealsense2 as rs

class CalibratorCheckBox(py_trees.behaviour.Behaviour):
    def __init__(self, window):
        self.window = window
        super().__init__("CalibratorCheckBox")

    def update(self) -> common.Status:
        return self.status.SUCCESS if self.window.checkBox.isChecked() else self.status.FAILURE


class Calibrator(py_trees.behaviour.Behaviour):
    def __init__(self, cam, window):
        self.window = window
        self.cam = cam
        self.camInputTxt = self.window.pixelInput
        self.cobotInputTxt = self.window.input
        super().__init__("PixelCalibrator")


    def transform_to_world_coordinates(self, x, y, depth, intrin):
        # Convert pixel coordinates to 3D world coordinates
        pixel = np.array([x, y])
        depth_point = rs.rs2_deproject_pixel_to_point(intrin, pixel, depth)

        return depth_point

    def getWorldCoord(self, pixel, depth_intrin):
        pixel_distance = self.cam.depth_frame.get_distance(pixel[0], pixel[1])
        camera_coordinates = self.transform_to_world_coordinates(pixel[0], pixel[1],
                                                                 pixel_distance, depth_intrin)
        cameraPose = [1000 * camera_coordinates[0], 1000 * camera_coordinates[1], 1000 * camera_coordinates[2]]
        cameraPose = np.array(cameraPose)
        return cameraPose

    def isValidInput(self, text):
        if not "," in text:
            return False
        data = list(map(float, text.split(",")))
        return len(data) == 2
    def update(self):
        camText = self.camInputTxt.text()
        if not self.isValidInput(camText):
            return self.status.RUNNING


        depth_intrin = self.cam.depth_frame.profile.as_video_stream_profile().intrinsics
        centerPixel = list(map(float, camText.split(',')))
        centerPixel = list(map(int, centerPixel))
        cameraPose = self.getWorldCoord(centerPixel, depth_intrin)
        line = f"{cameraPose[0]:.2f},{cameraPose[1]:.2f}"
        self.window.calibrationLine.put(line)
        self.logger.info(line)

        return self.status.SUCCESS