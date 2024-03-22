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

    def update(self) -> common.Status:

        depth_intrin = self.cam.depth_frame.profile.as_video_stream_profile().intrinsics
        msg = ""
        for objName, boxes in self.detector.detections.items():
            for b in boxes:
                pixel_distance = self.cam.depth_frame.get_distance(int((b[0] + b[2]) / 2), int((b[1] + b[3]) / 2))
                world_coordinates = self.transform_to_world_coordinates(int((b[0] + b[2]) / 2), int((b[1] + b[3]) / 2),
                                                                        pixel_distance, depth_intrin)
                world_coordinates_mm = [1000 * world_coordinates[0], 1000 * world_coordinates[1], 1000 * world_coordinates[2]]
                self.logger.info(f"{objName} world coordinate ({ world_coordinates_mm}) mm")
                msg += f"{objName},{world_coordinates_mm[0]},{world_coordinates_mm[1]},{world_coordinates_mm[2]}\n"
        self.pub.set("/%s/state" % self.name, msg)
        self.detector.detections.clear()
        return self.status.SUCCESS
