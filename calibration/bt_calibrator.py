import py_trees
import py_trees.console as console
import numpy as np
from py_trees import common
from scipy.optimize import least_squares
class Calibrator(py_trees.behaviour.Behaviour):
    def __init__(self, ax, canvas, table, msgbox):
        self.ax = ax
        self.canvas = canvas
        self.table = table
        self.msgbox = msgbox
        self.clicked = False
        super(Calibrator, self).__init__('Calibrator')

    def point_transformation(self, point, origin):
        x = (point - origin)
        x[1] *= -1
        return x

    def computeOptimalTransformation(self, camera, cobot):

        def calibrate(x0_param, xx, y):
            y_hat = np.array([self.point_transformation(x, x0_param) for x in xx])
            return np.linalg.norm(y_hat - y)

        def find_transformation(camera, cobot):
            # initial guess on the parameters
            x0 = np.array([0.0, 0.0])
            res_lsq = least_squares(calibrate, x0, args=(camera, cobot))


            return np.array([res_lsq.x[0], res_lsq.x[1]])

        return find_transformation(camera, cobot)
    def update(self) -> common.Status:
        if not self.clicked:
            return self.status.FAILURE

        cobot, realsense = self.table.cobot, self.table.realsense

        # compute optimal transformation
        origin = self.computeOptimalTransformation(realsense, cobot)

        transformedData = realsense.copy()
        for i, p in enumerate(transformedData):
            transformedData[i] = self.point_transformation(p, origin)

        # show it to text box
        msg = f"x = {origin[0]:.3f}, y = {origin[1]:.3f}"
        self.logger.info(msg)
        self.msgbox.setPlainText(msg)

        # plot them
        self.ax.fill(cobot[:, 0], cobot[:, 1], 'y', alpha=0.4)
        self.ax.fill(realsense[:, 0], realsense[:, 1], 'b')
        self.ax.fill(transformedData[:, 0], transformedData[:, 1], 'r', alpha=0.4)

        self.ax.legend(['cobot', 'realsense', 'transformed'])
        self.canvas.draw()
        self.clicked = False
        return self.status.SUCCESS