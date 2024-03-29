import py_trees
from py_trees import common
import numpy as np
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
        if event.inaxes:
            print('Mouse click at x={:.3f}, y={:.3f}'.format(event.xdata, event.ydata))
            # self.query = [event.xdata, event.ydata]
            if len(self.grid.objCoord) == 0:
                print("[+] creating event data")
                self.grid.objCoord.append(event.xdata)
                self.grid.objCoord.append(event.ydata)
                self.__intialized = True
                self.plot(self.grid.objCoord)
            elif len(self.grid.objCoord) == 2:
                print("[+] updating event data")
                self.grid.objCoord[0] = event.xdata
                self.grid.objCoord[1] = event.ydata
            else:
                print("[-] Failed to update event data")


    def plot(self, query):

        if len(query) != 2:
            self.ax.cla()
            self.ax.fill(self.grid.workspace[:, 0], self.grid.workspace[:, 1], 'y', alpha=0.4)
            self.ax.scatter(self.grid.grid_cells[:, 0], self.grid.grid_cells[:, 1], c='k', s=10)
            self.ax.plot(np.hstack((self.grid.bbox[:, 0], self.grid.bbox[0, 0])),
                         np.hstack((self.grid.bbox[:, 1], self.grid.bbox[0, 1])))

            self.canvas.draw()
            return

        cellId = self.grid.getCellId(query)
        if self.lastCellId is not None and self.lastCellId == cellId:
            return
        self.lastCellId = cellId
        cellCoord = self.grid.getCellCoord(cellId)


        self.ax.cla()
        self.ax.fill(self.grid.workspace[:, 0], self.grid.workspace[:, 1], 'y', alpha=0.4)
        self.ax.scatter(self.grid.grid_cells[:, 0], self.grid.grid_cells[:, 1], c='k', s=10)
        self.ax.plot(np.hstack((self.grid.bbox[:, 0], self.grid.bbox[0, 0])), np.hstack((self.grid.bbox[:, 1], self.grid.bbox[0, 1])))

        self.ax.scatter(query[0], query[1], s=15)
        self.ax.scatter(cellCoord[0], cellCoord[1], s=20, c='r')
        self.canvas.draw()

    def update(self) -> common.Status:
        self.plot(self.grid.objCoord)
        return self.status.SUCCESS if self.__intialized else self.status.FAILURE