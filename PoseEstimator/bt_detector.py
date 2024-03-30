import threading

import py_trees
import py_trees.console as console
from py_trees import common
from collections import defaultdict
from threading import Thread

class Detector(py_trees.behaviour.Behaviour):
    def __init__(self, camera,enable_func, model_path, threshold=0.5):
        self.camera = camera
        self.enabled = enable_func
        self.__model_loaded = False
        self.__busy = False
        self.model_path = model_path
        self.threshold = threshold
        super().__init__("Detector")
        self.detections = defaultdict(list)
        self.pub = py_trees.blackboard.Client(name=self.name, namespace=self.name)
        self.pub.register_key(key="/%s/state" % self.name, access=py_trees.common.Access.WRITE)

        t = Thread(target=self.load_model)
        t.start()

    def load_model(self):
        console.info(console.red + "Loading model..." + console.reset)
        from ultralytics import YOLO
        self.model = YOLO(self.model_path)
        self.__model_loaded = True
        console.info(console.green + "Loading complete..." + console.reset)

    def detect(self):
        self.__busy = True
        image = self.camera.color_image.copy()
        results = self.model(image, verbose=False)

        msg = ""
        for r in results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0].to(
                    'cpu').detach().numpy().copy()  # get box coordinates in (top, left, bottom, right) format
                c = self.model.names[int(box.cls)]
                s = float(box.conf)
                if s >= self.threshold:
                    # self.logger.info(f" cls = {c} | box = {b} | confidence = {s:.3f}")
                    msg += f"{c},{s:.3f},{b[0]},{b[1]},{b[2]},{b[3]}\n"

                    self.detections[c].append(b)

        if len(self.detections) > 0:
            self.pub.set("/%s/state" % self.name, msg)

        self.__busy = False



    def update(self) -> common.Status:
        if not self.enabled():
            return self.status.FAILURE

        if not self.__model_loaded or self.camera.color_image is None or self.__busy:
            return self.status.FAILURE

        detectThread = Thread(target=self.detect)
        detectThread.start()
        if len(self.detections) > 0:
            return self.status.SUCCESS
        return self.status.FAILURE