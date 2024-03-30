import py_trees
from py_trees import common
import numpy as np
from matplotlib.patches import Circle, Rectangle
class ControlInput(py_trees.behaviour.Behaviour):
    def __init__(self, ax, canvas, grid):
        self.ax = ax
        self.canvas = canvas

        self.grid = grid
        # Connect the mouse click event
        self.canvas.mpl_connect('button_press_event', self.onclick)
        super(ControlInput, self).__init__("ControlInput")
        self.lastCellId = None
        self.__intialized = False




    def getGridCoord(self, point):
        idx = self.grid.getCellId(point)
        coord = self.grid.getCellCoord(idx)
        return coord

    def onclick(self, event):
        if event.inaxes and len(self.grid.objCoord) == 0:
            if len(self.grid.objCoord) == 0:
                print('[Task] Pick Obj x={:.3f}, y={:.3f}'.format(event.xdata, event.ydata))
                gridCoord = self.getGridCoord([event.xdata, event.ydata])
                self.grid.objCoord.append(gridCoord[0])
                self.grid.objCoord.append(gridCoord[1])
                self.ax.cla()
                self.__plt_background()
                self.ax.set_title("[Task] Pick Obj ({:.2f}, {:.2f})".format(event.xdata, event.ydata))
                self.canvas.draw()
            else:
                print("[-] Failed to update event data")
        elif len(self.grid.objCoord) != 0:
            print("[!] Input Rejected")
            # self.ax.set_title("[!] Input Rejected")
            # self.canvas.draw()

    def __plt_background(self):
        radius = self.grid.offsetRadius - self.grid.gridResolution
        boxOrigin = (self.grid.bbox[0] - self.grid.gridResolution / 2.0, self.grid.bbox[2] - self.grid.gridResolution / 2.0)
        boxWidth = self.grid.bbox[1] - self.grid.bbox[0] + self.grid.gridResolution
        boxHeight = self.grid.bbox[3] - self.grid.bbox[2] + self.grid.gridResolution
        self.ax.scatter(self.grid.grid_cells[:, 0], self.grid.grid_cells[:, 1], c='m', s=10)
        circle = Circle((0, 0), radius=radius, color='k', alpha=0.8)
        bbox = Rectangle(boxOrigin, boxWidth, boxHeight, fill=False, edgecolor='m', linewidth=2)
        self.ax.add_patch(circle)
        self.ax.add_patch(bbox)

        if len(self.grid.objCoord) == 2:
            self.ax.scatter(self.grid.objCoord[0], self.grid.objCoord[1], s=50, c='r')

        self.ax.axis('square')
        self.ax.axis('off')

    def plot(self, query):

        if len(query) != 2 and not self.__intialized:
            self.ax.cla()
            self.__plt_background()
            self.canvas.draw()
            self.__intialized = True
            return


    def update(self) -> common.Status:
        self.plot(self.grid.objCoord)
        return self.status.SUCCESS if self.__intialized else self.status.FAILURE