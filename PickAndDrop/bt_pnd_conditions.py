import py_trees
from py_trees import common

class DeliveryCondition(py_trees.behaviour.Behaviour):
    def __init__(self, objCoord, grid_world, name):
        self.objCoord = objCoord
        self.grid_world = grid_world
        super().__init__(name)

    def update(self) -> common.Status:
        if self.grid_world.getCellId(self.objCoord) == self.grid_world.deliveryCellIdx:
            return self.status.SUCCESS
        # self.logger.info("delivery request @ {}".format(self.objCoord))
        return self.status.FAILURE

class HandCondition(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        self._inHand = False
        super().__init__(name)

    def update(self) -> common.Status:
        return self.status.SUCCESS if self._inHand else self.status.FAILURE

class RobotAtSrcCondition(py_trees.behaviour.Behaviour):
    def __init__(self, robotCoord, objCoord, grid_world, name):
        self.robotCoord = robotCoord
        self.grid_world = grid_world
        self.objCoord = objCoord
        super().__init__(name)

    def update(self) -> common.Status:
        self.logger.info(f"RobotAtSrcCondition {self.grid_world.deliveryCellCoord} | {self.robotCoord}, goal = {self.grid_world.getCellId(self.objCoord)} robot = {self.grid_world.getCellId(self.robotCoord)}")
        if self.grid_world.getCellId(self.objCoord) == self.grid_world.getCellId(self.robotCoord):
            self.logger.info(f"RobotAtSrcCondition SUCCESS")
            return self.status.SUCCESS
        return self.status.FAILURE

class RobotAtDeliveryCondition(py_trees.behaviour.Behaviour):
    def __init__(self,robotCoord, grid_world, name):
        self.robotCoord = robotCoord
        self.grid_world = grid_world
        super().__init__(name)

    def update(self) -> common.Status:
        self.logger.info(
            f"RobotAtDeliveryCondition {self.robotCoord}, goal = {self.grid_world.deliveryCellIdx} robot = {self.grid_world.getCellId(self.robotCoord)}")

        if self.grid_world.deliveryCellIdx == self.grid_world.getCellId(self.robotCoord):
            self.logger.info(f"Robot at delivery {self.robotCoord}")
            self.logger.info(f"RobotAtDeliveryCondition SUCCESS")
            return self.status.SUCCESS
        return self.status.FAILURE