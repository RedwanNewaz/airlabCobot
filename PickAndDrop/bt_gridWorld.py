import numpy as np
import py_trees
from py_trees import common
import cv2

class GridWorld(py_trees.behaviour.Behaviour):
    def __init__(self, config):
        self.parseConfig(config)
        self.__initialized = False
        self.objCoord = []
        super(GridWorld, self).__init__("GridWorld")

    def parseConfig(self, config):
        self.bbox = list(map(float, config.get("workspace").split(",")))
        self.offsetRadius = float(config.get("offsetRadius"))
        self.gridResolution = int(config.get("resolution"))
        self.deliveryCellCoord = list(map(float, config.get("deliveryCellCoord").split(",")))

    def discretize_bbox_into_grid(self, desire_resolution):

        X = np.linspace(self.bbox[0], self.bbox[1], desire_resolution)
        Y = np.linspace(self.bbox[2], self.bbox[3], desire_resolution)

        grid_cells = []
        for y in Y:
            for x in X:
                p = np.array([x, y])
                d = np.linalg.norm(p)
                if d > 150.0:
                    grid_cells.append(p)
        return np.array(grid_cells)

    def getCellId(self, p):
        q = p.copy()
        if not isinstance(q, np.ndarray):
            q = np.array(q)
        relPos = self.grid_cells - q
        dist = np.linalg.norm(relPos, axis=1)
        idx = np.argmin(dist)
        return idx

    def getCellCoord(self, idx):
        assert idx < len(self.grid_cells)
        return self.grid_cells[idx]

    # Get mouse coordinates interactively

    def update(self) -> common.Status:
        if self.__initialized:
            return self.status.FAILURE


        self.grid_cells = self.discretize_bbox_into_grid(self.gridResolution)
        self.logger.info(f'num grid cells {len(self.grid_cells)}')
        self.__initialized = True
        self.deliveryCellIdx = self.getCellId(self.deliveryCellCoord)
        return self.status.SUCCESS