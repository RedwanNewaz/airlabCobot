import py_trees
from py_trees import common
import numpy as np
import pyrealsense2 as rs


class PoseEstimator(py_trees.behaviour.Behaviour):
    def __init__(self, cam, detector):
        self.cam = cam
        self.detector = detector
        super().__init__("PoseEstimator")
        self.pub = py_trees.blackboard.Client(name=self.name, namespace=self.name)
        self.pub.register_key(key="/%s/state" % self.name, access=py_trees.common.Access.WRITE)

    def transform_to_world_coordinates(self, x, y, depth, intrin):
        # Convert pixel coordinates to 3D world coordinates
        pixel = np.array([x, y])
        depth_point = rs.rs2_deproject_pixel_to_point(intrin, pixel, depth)

        return depth_point

    def toRobotCoord(self, cameraPose):
        p = np.array([347, 709, 0.46])
        # p = np.array([-285, -261, 0.46])
        T = p[:2]
        theta = p[-1]
        R = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])
        return T + R @ cameraPose

    def update(self) -> common.Status:

        depth_intrin = self.cam.depth_frame.profile.as_video_stream_profile().intrinsics
        msg = ""
        for objName, boxes in self.detector.detections.items():
            for b in boxes:
                pixel_distance = self.cam.depth_frame.get_distance(int((b[0] + b[2]) / 2), int((b[1] + b[3]) / 2))
                camera_coordinates = self.transform_to_world_coordinates(int((b[0] + b[2]) / 2), int((b[1] + b[3]) / 2),
                                                                        pixel_distance, depth_intrin)
                cameraPose = [1000 * camera_coordinates[0], 1000 * camera_coordinates[1], 1000 * camera_coordinates[2]]
                cameraPose = np.array(cameraPose)
                world_coordinates_mm = self.toRobotCoord(cameraPose[:2])

                # self.logger.info(f"{objName} world coordinate ({ world_coordinates_mm}) mm")
                msg += f"{objName},{world_coordinates_mm[0]:.2f},{world_coordinates_mm[1]:.2f}\n"
        self.pub.set("/%s/state" % self.name, msg)
        self.detector.detections.clear()
        return self.status.SUCCESS
