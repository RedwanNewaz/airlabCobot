from matplotlib import pyplot as plt
import numpy as np
from scipy.optimize import least_squares

def point_transformation(x, p):
  T = p[:2]
  theta = p[-1]
  R = np.array([[np.cos(theta), -np.sin(theta)],
                [np.sin(theta), np.cos(theta)]])
  Q = R @ x + T

  return Q


def calibrate(x0_param, xx, y):
  y_hat = np.array([point_transformation(x, x0_param) for x in xx])
  return np.linalg.norm(y_hat - y)

def plot_data(cobot, camera):
    plt.fill(cobot[:, 0], cobot[:, 1], 'r')
    plt.fill(camera[:, 0], camera[:, 1], 'b')

    COLORS = ['k', 'g', 'm', 'cyan', 'green', 'red', 'blue']
    for i, p in enumerate(cobot):
        plt.scatter(p[0], p[1], color=COLORS[i])

    for i, p in enumerate(camera):
        plt.scatter(p[0], p[1], color=COLORS[i])

    plt.show()

def find_transformation(camera, cobot):
    # initial guess on the parameters
    x0 = np.array([0.0, 0.0, 0.0])
    res_lsq = least_squares(calibrate, x0, args=(camera, cobot))

    print(
        f"x = {res_lsq.x[0]:.3f}, y = {res_lsq.x[1]:.3f}, theta = {res_lsq.x[2]:.3f} "
    )


if __name__ == '__main__':
    cobot = np.loadtxt('cobot1.txt', delimiter=',') / 100.0
    camera = np.loadtxt('realsense2.txt', delimiter=',')[:, :2] / 100.0

    # x0 = np.array([-2.845, 3.0, 0.0])
    x0 = np.array([-3.593, -2.944, 1.578 ])

    for i, p in enumerate(camera):
        camera[i] = point_transformation(p, x0)
    #
    # camera = np.flipud(camera)
    find_transformation(camera, cobot)
    # camera = np.fliplr(camera)
    camera = np.flipud(camera)
    # camera = np.fliplr(camera)



    plot_data(cobot, camera)



