import py_trees
import py_trees.console as console
import pyrealsense2 as rs
import numpy as np
import cv2


class Camera(py_trees.behaviour.Behaviour):
    def __init__(self, ax, window):
        W = 640
        H = 480

        self.ax = ax
        self.window = window
        self.color_image = None
        config = rs.config()
        config.enable_stream(rs.stream.color, W, H, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, W, H, rs.format.z16, 30)

        self.pipeline = rs.pipeline()
        profile = self.pipeline.start(config)

        align_to = rs.stream.color
        self.align = rs.align(align_to)
        super().__init__(f"camera")

    @staticmethod
    def check_bounding_box():
        input_string = py_trees.display.unicode_blackboard(key_filter={"/Detector/state"})
        lines = input_string.strip().split('\n')
        for line in lines:
            if ":"  in line or "state"  in line or 'Data' in line:
                continue
            msg_parse = line.strip().split(',')
            yield msg_parse


    def draw(self):
        self.ax.clear()
        destRGB = cv2.cvtColor(self.color_image, cv2.COLOR_BGR2RGB)
        data = []
        for detection in self.check_bounding_box():
            b = list(map(int, map(float, detection[2:])))
            data.append([detection[0], detection[1]])
            if len(b) == 4:
                cv2.rectangle(destRGB, (b[0], b[1]), (b[2], b[3]), (0, 0, 255),
                              thickness=2, lineType=cv2.LINE_4)
                cv2.putText(destRGB, text=detection[0], org=(b[0], b[1]),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 0, 255),
                            thickness=2, lineType=cv2.LINE_4)


        self.ax.imshow(destRGB)
        self.ax.axis('off')
        if len(data) > 0:
            self.window.populate_table(data)
        # Refresh canvas
        self.window.canvas.draw()

    def update(self):
        frames = self.pipeline.wait_for_frames()

        aligned_frames = self.align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        self.depth_frame = aligned_frames.get_depth_frame()
        if color_frame:
            #TODO communicate

            self.color_image = np.asanyarray(color_frame.get_data())
            self.depth_image = np.asanyarray(self.depth_frame.get_data())
            self.draw()

            return self.status.SUCCESS
        return self.status.FAILURE