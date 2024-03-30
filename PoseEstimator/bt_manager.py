import py_trees.console as console
import py_trees
from .bt_cam import Camera
from .bt_viewer import Viewer
from .bt_calibrator import CalibratorCheckBox, Calibrator
from .bt_tracking import TrackingCheckBox, Tracking
from .bt_detector import Detector
from .bt_pose_estimator import PoseEstimator
from threading import Thread

class NodeManager(Thread):
    def __init__(self, ax, window, model_path, config):
        Thread.__init__(self)
        self.window = window
        cam = Camera()
        viewer = Viewer(cam, ax, window)
        checkbox = CalibratorCheckBox(window)
        calibrator = Calibrator(cam, window)

        seq_calibrator = py_trees.composites.Sequence(name="seq_calibrator", memory=True)
        seq_calibrator.add_children([checkbox, calibrator])

        trackingCheckbox = TrackingCheckBox(window)
        tracking = Tracking(window)
        seq_tracking = py_trees.composites.Sequence(name="seq_tracking", memory=True)
        seq_tracking.add_children([trackingCheckbox, tracking])

        selector_calibrator = py_trees.composites.Selector(name="selector_calibrator", memory=True)
        selector_calibrator.add_children([seq_tracking, seq_calibrator])

        detector = Detector(cam, window.trackingBox.isChecked, model_path)
        origin = config['REALSENSE']['origin']
        origin = list(map(float, origin.split(',')))
        pose_estimator = PoseEstimator(cam, detector, origin)

        seq_camera = py_trees.composites.Sequence(name="seq_camera", memory=True)
        seq_camera.add_children([cam, viewer, selector_calibrator])

        seq_detector = py_trees.composites.Sequence(name="seq_detector", memory=True)
        seq_detector.add_children([detector, pose_estimator])




        root = py_trees.composites.Parallel(
            name="airlabCobot",
            # policy=py_trees.common.ParallelPolicy.SuccessOnAll()
            # policy=py_trees.common.ParallelPolicy.SuccessOnOne()
            policy=py_trees.common.ParallelPolicy.SuccessOnSelected([seq_detector])
        )

        # root = py_trees.composites.Selector("PoseSelector", True)

        root.add_children([seq_camera, seq_detector])


        task = py_trees.composites.Sequence("Sequence", True)
        task.add_child(root)
        self.behaviour_tree = py_trees.trees.BehaviourTree(task)
        self.terminate = False

    def run(self):
        while not self.window.terminated or self.terminate:
            self.behaviour_tree.tick()
        print("[PoseEsitmator] terminated ... ")
