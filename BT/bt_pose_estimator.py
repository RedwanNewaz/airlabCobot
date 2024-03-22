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

    def toRobotCoord(self, point):
        origin = np.array([294.423, -362.489, 0.0])
        x = (point - origin)
        x[1] *= -1
        return x


    def getWorldCoord(self, pixel, depth_intrin):
        pixel_distance = self.cam.depth_frame.get_distance(pixel[0], pixel[1])
        camera_coordinates = self.transform_to_world_coordinates(pixel[0], pixel[1],
                                                                 pixel_distance, depth_intrin)
        cameraPose = [1000 * camera_coordinates[0], 1000 * camera_coordinates[1], 1000 * camera_coordinates[2]]
        cameraPose = np.array(cameraPose)
        return cameraPose

    def update(self) -> common.Status:

        depth_intrin = self.cam.depth_frame.profile.as_video_stream_profile().intrinsics
        msg = ""
        for objName, boxes in self.detector.detections.items():
            for b in boxes:
                centerPixel = [int((b[0] + b[2]) / 2), int((b[1] + b[3]) / 2)]
                # centerPixel = [416, 133]
                cameraPose = self.getWorldCoord(centerPixel, depth_intrin)

                # msg += f"{objName},{cameraPose[0]:.2f},{cameraPose[1]:.2f}\n"
                robotPose = self.toRobotCoord(cameraPose)
                msg += f"{objName},{robotPose[0]:.2f},{robotPose[1]:.2f}\n"
        self.pub.set("/%s/state" % self.name, msg)
        self.detector.detections.clear()
        return self.status.SUCCESS
