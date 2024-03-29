import threading

import py_trees
from py_trees import common
import time
class MoveToSrc(py_trees.behaviour.Behaviour):
    def __init__(self, robot, objCoord, name):
        self.robot = robot
        self.objCoord = objCoord
        self.__start_time = None

        super().__init__(name)


    def update(self) -> common.Status:

        # if len(self.objCoord) != 2:
        #     self.__start_time = None
        #     # self.logger.info(f"[Finish] moving to src")
        #     return self.status.FAILURE

        # elif self.__start_time is None:
        #     self.robot.setPoint = self.objCoord.copy()
        #
        #     if self.robot.task_move():
        #         self.logger.info(f"[Start] moving to src @ ({self.objCoord[0]:.3f}, {self.objCoord[1]:.3f})")
        #         self.__start_time = time.time()
        #     return self.status.RUNNING
        if not self.robot.done:
            self.robot.setPoint = self.objCoord.copy()
            if self.robot.task_move():
                self.logger.info(f"[Start] moving to src @ ({self.objCoord[0]:.3f}, {self.objCoord[1]:.3f})")
                self.__start_time = time.time()
            return self.status.RUNNING

        return self.status.SUCCESS

class PickObject(py_trees.behaviour.Behaviour):
    def __init__(self, robot, check_hand, name):
        self.robot = robot
        self.check_hand = check_hand
        self.duration = 1 # sec
        self.__start_time = None
        super().__init__(name)

    def update(self) -> common.Status:
        if not self.robot._pick:
            self.__start_time = time.time()
            if self.robot.task_pick():
                self.logger.info(f"picking up object")
            # self.robot.done = False

            return self.status.FAILURE
        return self.status.SUCCESS

class MoveToDelivery(py_trees.behaviour.Behaviour):
    def __init__(self, robot, grid_world, objCoord, name):
        self.robot = robot
        self.grid_world = grid_world
        self.objCoord = objCoord

        super().__init__(name)

    def update(self) -> common.Status:
        if not self.robot.done:
            self.robot.setPoint = self.grid_world.deliveryCellCoord.copy()
            if self.robot.task_move():
                self.logger.info(f"[+] start moving to {self.grid_world.deliveryCellCoord}")
                self.robot.done = False
            return self.status.RUNNING


        return self.status.SUCCESS

class PlaceObject(py_trees.behaviour.Behaviour):
    def __init__(self, robot, objCoord, grid_world, name):
        self.robot = robot
        self.objCoord = objCoord
        self.grid_world = grid_world
        self.__start_time = None

        super().__init__(name)

    def update(self) -> common.Status:
        if self.robot._pick:
            self.__start_time = time.time()
            if self.robot.task_drop():
                self.logger.info(f"dropping object")
            return self.status.RUNNING
        self.robot._pick = False
        return self.status.SUCCESS