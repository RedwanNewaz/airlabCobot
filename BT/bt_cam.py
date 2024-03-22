import py_trees
import py_trees.console as console
import pyrealsense2 as rs
import numpy as np
import cv2


class Camera(py_trees.behaviour.Behaviour):
    def __init__(self):
        W = 640
        H = 480
        self.color_image = None
        config = rs.config()
        config.enable_stream(rs.stream.color, W, H, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, W, H, rs.format.z16, 30)

        self.pipeline = rs.pipeline()
        profile = self.pipeline.start(config)

        align_to = rs.stream.color
        self.align = rs.align(align_to)
        super().__init__(f"camera")


    def update(self):
        frames = self.pipeline.wait_for_frames()

        aligned_frames = self.align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        self.depth_frame = aligned_frames.get_depth_frame()
        if color_frame:
            #TODO communicate

            self.color_image = np.asanyarray(color_frame.get_data())
            self.depth_image = np.asanyarray(self.depth_frame.get_data())
            return self.status.SUCCESS
        return self.status.FAILURE