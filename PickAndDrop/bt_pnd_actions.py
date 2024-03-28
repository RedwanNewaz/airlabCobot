import py_trees
from py_trees import common
import time
from threading import Thread
class MoveToSrc(py_trees.behaviour.Behaviour):
    def __init__(self, robot, objCoord, name):
        self.objCoord = objCoord
        self.duration = 2  # sec
        self.__start_time = None
        self.robot = robot
        self.done = True
        super().__init__(name)

    def move(self):
        self.done = False
        self.robot.move(self.objCoord)
        self.done = True

        print('move to src done')

    def update(self) -> common.Status:

        if self.__start_time is None and self.done:
            self.__start_time = time.time()
            self.logger.info(f"moving to src @ ({self.objCoord[0]:.3f}, {self.objCoord[1]:.3f})")
            self.__thread = Thread(target=self.move)
            self.__thread.start()
            return self.status.RUNNING
        elif time.time() - self.__start_time < self.duration or not self.done:
            return self.status.RUNNING
        self.__start_time = None
        return self.status.SUCCESS

class PickObject(py_trees.behaviour.Behaviour):
    def __init__(self, robot, check_hand, name):
        self.robot = robot
        self.check_hand = check_hand
        self.duration = 2 # sec
        self.__start_time = None

        self.done = True
        super().__init__(name)

    def pick(self):
        self.done = False
        self.robot.pick()
        self.done = True

    def update(self) -> common.Status:
        if self.__start_time is None and self.done:
            self.__start_time = time.time()
            self.logger.info(f"picking up object")
            self.__thread = Thread(target=self.pick)
            self.__thread.start()
            return self.status.RUNNING
        elif time.time() - self.__start_time < self.duration or not self.done:
            return self.status.RUNNING
        self.check_hand._inHand = True
        self.__start_time = None
        return self.status.SUCCESS

class MoveToDelivery(py_trees.behaviour.Behaviour):
    def __init__(self, robot, grid_world, objCoord, name):
        self.robot = robot
        self.grid_world = grid_world
        self.objCoord = objCoord
        self.duration = 2  # sec
        self.__start_time = None
        self.done = True
        super().__init__(name)

    def move(self):
        self.done = False
        self.robot.move(self.grid_world.deliveryCellCoord)
        self.done = True


    def update(self) -> common.Status:
        if self.__start_time is None and self.done:
            self.__start_time = time.time()
            self.logger.info(f"moving to {self.grid_world.deliveryCellCoord}")
            self.__thread = Thread(target=self.move)
            self.__thread.start()
            return self.status.RUNNING
        elif time.time() - self.__start_time < self.duration or not self.done:
            return self.status.RUNNING

        self.objCoord[0] = self.grid_world.deliveryCellCoord[0]
        self.objCoord[1] = self.grid_world.deliveryCellCoord[1]
        self.__start_time = None
        return self.status.SUCCESS

class PlaceObject(py_trees.behaviour.Behaviour):
    def __init__(self, robot, check_hand, name):
        self.robot = robot
        self.duration = 2  # sec
        self.__start_time = None
        self.check_hand = check_hand
        self.done = True
        super().__init__(name)

    def drop(self):
        self.done = False
        self.robot.drop()
        self.done = True


    def update(self) -> common.Status:
        if self.__start_time is None and self.done:
            self.__start_time = time.time()
            self.logger.info(f"dropping object")
            self.__thread = Thread(target=self.drop)
            self.__thread.start()
            return self.status.RUNNING
        elif time.time() - self.__start_time < self.duration or  not self.done:
            return self.status.RUNNING

        self.check_hand._inHand = False
        self.__start_time = None
        return self.status.SUCCESS