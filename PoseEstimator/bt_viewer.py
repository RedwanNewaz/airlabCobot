import py_trees
import py_trees.console as console
import numpy as np
import cv2

class Viewer(py_trees.behaviour.Behaviour):
    def __init__(self, cam, ax, window):
        self.cam = cam
        self.ax = ax
        self.window = window
        super().__init__("Viewer")

    @staticmethod
    def check_bounding_box():
        input_string = py_trees.display.unicode_blackboard(key_filter={"/Detector/state"})
        lines = input_string.strip().split('\n')
        for line in lines:
            if ":" in line or "state" in line or 'Data' in line:
                continue
            msg_parse = line.strip().split(',')
            yield msg_parse

    def update(self):

        if self.window.checkBox.isChecked():
            return self.status.FAILURE

        self.ax.clear()
        destRGB = cv2.cvtColor(self.cam.color_image, cv2.COLOR_BGR2RGB)
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
        return self.status.SUCCESS