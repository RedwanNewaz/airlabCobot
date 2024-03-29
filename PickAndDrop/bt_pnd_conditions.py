import py_trees
from py_trees import common

class DeliveryCondition(py_trees.behaviour.Behaviour):
    def __init__(self, objCoord, robot, grid_world, name):
        self.objCoord = objCoord
        self.robot = robot
        self.grid_world = grid_world
        super().__init__(name)

    def update(self) -> common.Status:

        if len(self.objCoord) and self.grid_world.getCellId(self.objCoord) == self.grid_world.deliveryCellIdx:
            # self.logger.warning("delivery request @ {}".format(self.objCoord))
            return self.status.SUCCESS
        elif len(self.objCoord) != 2:
            self.robot.done = False
            self.robot._pick = False
            return self.status.RUNNING

        # self.logger.info("delivery request @ {}".format(self.objCoord))
        return self.status.FAILURE

class HandCondition(py_trees.behaviour.Behaviour):
    def __init__(self, robot, name):
        self._inHand = False
        self.robot = robot
        super().__init__(name)

    def update(self) -> common.Status:
        # self.logger.info(f"[+] Pick up task completed {self.robot._pick}")
        if self.robot._pick:
            # self.robot.done = False
            return self.status.SUCCESS
        return self.status.FAILURE

class RobotAtSrcCondition(py_trees.behaviour.Behaviour):
    def __init__(self, robot, objCoord, grid_world, name):
        self.robot = robot
        self.grid_world = grid_world
        self.objCoord = objCoord
        super().__init__(name)

    def update(self) -> common.Status:
        # if self.grid_world.getCellId(self.objCoord) == self.grid_world.getCellId(self.robotCoord):
        #     return self.status.SUCCESS
        # if len(self.objCoord) != 2:
        #
        #     self.robot._pick = False
        #     return self.status.FAILURE

        if self.robot.done:
            self.logger.info(f"[+] robot reach at src {self.robot.done}")
            self.robot.done = False
            return self.status.SUCCESS
        return self.status.FAILURE
class RobotAtDeliveryCondition(py_trees.behaviour.Behaviour):
    def __init__(self,robot, objCoord, grid_world, name):
        self.objCoord = objCoord
        self.robot = robot
        self.grid_world = grid_world
        super().__init__(name)


    def update(self) -> common.Status:
        if self.robot.done:
            self.logger.info(f"[+Finish] robot reach at destination {self.robot._pick}")
            self.robot.done = False
            self.objCoord.clear()
            return self.status.SUCCESS
        return self.status.FAILURE