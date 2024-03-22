from matplotlib import pyplot as plt
import numpy as np
from scipy.optimize import least_squares

def point_transformation(x, p):
  T = p[:2]
  theta = p[-1]
  R = np.array([[np.cos(theta), -np.sin(theta)],
                [np.sin(theta), np.cos(theta)]])
  return T - R @ x


def calibrate(x0_param, xx, y):
  y_hat = np.array([point_transformation(x, x0_param) for x in xx])
  return np.linalg.norm(y_hat - y)

def plot_data(cobot, camera):
    plt.fill(cobot[:, 0], cobot[:, 1], 'r')
    plt.fill(camera[:, 0], camera[:, 1], 'b')
    plt.show()

def find_transformation(cobot, camera):
    # initial guess on the parameters
    x0 = np.array([0.0, 0.0, 0.0])
    res_lsq = least_squares(calibrate, x0, args=(camera, cobot))

    print(
        f"x = {res_lsq.x[0]:.3f}, y = {res_lsq.x[1]:.3f}, theta = {res_lsq.x[2]:.3f} "
    )


if __name__ == '__main__':
    cobot = np.loadtxt('cobot.txt', delimiter=',')
    camera = np.loadtxt('realsense.txt', delimiter=',')[:, :2]
    x0 = np.array([-285, -261, 0.46])
    for i, p in enumerate(camera):
        camera[i] = point_transformation(p, x0)

    plot_data(cobot, camera)



