import py_trees
from py_trees import common
import numpy as np
from matplotlib.patches import Circle, Rectangle
class SimPickDrop(py_trees.behaviour.Behaviour):
    def __init__(self, ax, canvas, grid):
        self.ax = ax
        self.canvas = canvas

        self.grid = grid
        # Connect the mouse click event
        self.canvas.mpl_connect('button_press_event', self.onclick)
        super(SimPickDrop, self).__init__("SimPickDrop")
        self.lastCellId = None
        self.__intialized = False


    def onclick(self, event):
        if event.inaxes and len(self.grid.objCoord) == 0:
            print('Mouse click at x={:.3f}, y={:.3f}'.format(event.xdata, event.ydata))
            # self.query = [event.xdata, event.ydata]
            if len(self.grid.objCoord) == 0:
                print("[+] creating event data")
                self.grid.objCoord.append(event.xdata)
                self.grid.objCoord.append(event.ydata)
                self.__intialized = True
                self.plot(self.grid.objCoord)
                self.ax.set_title("[Task] Pick Obj ({:.2f}, {:.2f})".format(event.xdata, event.ydata))
                self.canvas.draw()
            elif len(self.grid.objCoord) == 2:
                print("[+] updating event data")
                self.grid.objCoord[0] = event.xdata
                self.grid.objCoord[1] = event.ydata
            else:
                print("[-] Failed to update event data")
        elif len(self.grid.objCoord) != 0:
            print("[!] Input Rejected")
            self.ax.set_title("[!] Input Rejected")
            self.canvas.draw()

    def __plt_background(self):
        self.ax.scatter(self.grid.grid_cells[:, 0], self.grid.grid_cells[:, 1], c='m', s=10)
        circle = Circle((0, 0), radius=100.0, color='k', alpha=0.8)
        bbox = Rectangle((-205.0, -205.0), 410.0, 410.0, fill=False, edgecolor='m', linewidth=2)
        self.ax.add_patch(circle)
        self.ax.add_patch(bbox)
        self.ax.axis('square')

    def plot(self, query):

        if len(query) != 2:
            self.ax.cla()
            self.__plt_background()
            self.canvas.draw()
            return

        cellId = self.grid.getCellId(query)
        if self.lastCellId is not None and self.lastCellId == cellId:
            return
        self.lastCellId = cellId
        cellCoord = self.grid.getCellCoord(cellId)


        self.ax.cla()
        self.__plt_background()
        self.ax.scatter(query[0], query[1], s=35)
        self.ax.scatter(cellCoord[0], cellCoord[1], s=50, c='r')
        self.canvas.draw()

    def update(self) -> common.Status:
        self.plot(self.grid.objCoord)
        return self.status.SUCCESS if self.__intialized else self.status.FAILURE