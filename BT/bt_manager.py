import py_trees.console as console
import py_trees
from .bt_cam import Camera
from .bt_viewer import Viewer
from .bt_calibrator import Calibrator
from .bt_detector import Detector
from .bt_pose_estimator import PoseEstimator
from threading import Thread

class NodeManager(Thread):
    def __init__(self, ax, window, model_path):
        Thread.__init__(self)
        cam = Camera()
        viewer = Viewer(cam, ax, window)
        calibrator = Calibrator(window)

        detector = Detector(cam, model_path)
        pose_estimator = PoseEstimator(cam, detector)

        seq_camera = py_trees.composites.Sequence(name="seq_camera", memory=True)
        seq_camera.add_children([cam, viewer, calibrator])

        seq_detector = py_trees.composites.Sequence(name="seq_detector", memory=True)
        seq_detector.add_children([detector, pose_estimator])


        root = py_trees.composites.Parallel(
            name="airlabCobot",
            # policy=py_trees.common.ParallelPolicy.SuccessOnAll()
            # policy=py_trees.common.ParallelPolicy.SuccessOnOne()
            policy=py_trees.common.ParallelPolicy.SuccessOnSelected([seq_detector])
        )

        root.add_children([seq_camera, seq_detector])


        task = py_trees.composites.Sequence("Sequence", True)
        task.add_child(root)
        self.behaviour_tree = py_trees.trees.BehaviourTree(task)
        self.terminate = False

    def run(self):
        while not self.terminate:
            self.behaviour_tree.tick()
