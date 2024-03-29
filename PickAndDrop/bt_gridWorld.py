import numpy as np
import py_trees
from py_trees import common
import cv2

class GridWorld(py_trees.behaviour.Behaviour):
    def __init__(self, config):
        self.__initialized = False
        self.deliveryCellCoord = list(map(float, config["GRID"]["deliveryCellCoord"].split(",")))
        self.objCoord = []
        self.precision = int(config["GRID"]["precision"])
        self.gridResolution = int(config["GRID"]["resolution"])
        self.offset_x = float(config["GRID"]["offsetX"])
        self.offset_y = float(config["GRID"]["offsetY"])
        super(GridWorld, self).__init__("GridWorld")


    def loadData(self):
        rawData = np.loadtxt(f'calibration2.csv', delimiter=',').astype('str')
        cobot_data = [",".join(r) for r in rawData[:, :2]]
        data = []
        for item in cobot_data:
            data.append(list(map(float, item.split(','))))

        # realsense_data = [",".join(r) for r in rawData[:, 2:]]
        return np.array(data)

    def  min_rotated_box(self, workspace):
        points = workspace.copy() * self.precision
        points = points.astype(int)
        # Compute minimum area bounding rectangle
        rect = cv2.minAreaRect(points)

        # Get the box points
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        result = box.astype(float) / self.precision
        return result

    # Discretize bounding box into grid cells
    def discretize_bbox_into_grid(self, raw_bbox, desire_resolution):
        def sign(x):
            return -1.0 if x < 0 else 1.0
        grid_resolution = desire_resolution * self.precision
        bbox = raw_bbox * self.precision
        bbox = bbox.astype(int)
        # Determine min and max coordinates of bounding box
        min_x = min(bbox[:, 0])
        min_y = min(bbox[:, 1])
        max_x = max(bbox[:, 0])
        max_y = max(bbox[:, 1])

        # Iterate over each grid cell
        grid_cells = []
        for y in range(min_y, max_y, grid_resolution):
            for x in range(min_x, max_x, grid_resolution):
                grid_cell_center = np.array([x + grid_resolution / 2, y + grid_resolution / 2], dtype=np.float32)
                # Check if grid cell center is inside the bounding box
                if cv2.pointPolygonTest(bbox, tuple(grid_cell_center), False) >= 0:
                    # grid_cell = np.array([[x, y], [x + grid_resolution, y],
                    #                       [x + grid_resolution, y + grid_resolution],
                    #                       [x, y + grid_resolution]], dtype=np.int0)
                    # grid_cells.append(grid_cell)

                    if abs(grid_cell_center[0] / self.precision) < self.offset_x or abs(grid_cell_center[1] / self.precision) < self.offset_y:
                        continue

                    grid_cells.append(grid_cell_center)
        cells =  np.array(grid_cells).astype(float) / self.precision
        cells = np.clip(cells, -200.0, 200.0)
        return cells
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

        self.workspace = self.loadData()
        self.bbox = self.min_rotated_box(self.workspace)
        self.grid_cells = self.discretize_bbox_into_grid(self.bbox, self.gridResolution)
        self.logger.info(f'num grid cells {len(self.grid_cells)}')
        self.__initialized = True
        self.deliveryCellIdx = self.getCellId(self.deliveryCellCoord)
        return self.status.SUCCESS