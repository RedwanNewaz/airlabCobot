import py_trees
from py_trees import common
import time
class MoveToSrc(py_trees.behaviour.Behaviour):
    def __init__(self, objCoord, name):
        self.objCoord = objCoord
        self.duration = 1  # sec
        self.__start_time = None
        super().__init__(name)

    def update(self) -> common.Status:

        if self.__start_time is None:
            self.__start_time = time.time()
            self.logger.info(f"moving to src @ ({self.objCoord[0]:.3f}, {self.objCoord[1]:.3f})")
            return self.status.RUNNING
        elif time.time() - self.__start_time < self.duration:
            return self.status.RUNNING
        self.__start_time = None
        return self.status.SUCCESS

class PickObject(py_trees.behaviour.Behaviour):
    def __init__(self, check_hand, name):
        self.check_hand = check_hand
        self.duration = 1 # sec
        self.__start_time = None
        super().__init__(name)

    def update(self) -> common.Status:
        if self.__start_time is None:
            self.__start_time = time.time()
            self.logger.info(f"picking up object")
            return self.status.RUNNING
        elif time.time() - self.__start_time < self.duration:
            return self.status.RUNNING
        self.check_hand._inHand = True
        self.__start_time = None
        return self.status.SUCCESS

class MoveToDelivery(py_trees.behaviour.Behaviour):
    def __init__(self, grid_world, objCoord, name):
        self.grid_world = grid_world
        self.objCoord = objCoord
        self.duration = 1  # sec
        self.__start_time = None
        super().__init__(name)

    def update(self) -> common.Status:
        if self.__start_time is None:
            self.__start_time = time.time()
            self.logger.info(f"moving to {self.grid_world.deliveryCellCoord}")
            return self.status.RUNNING
        elif time.time() - self.__start_time < self.duration:
            return self.status.RUNNING
        self.__start_time = None


        self.objCoord[0] = self.grid_world.deliveryCellCoord[0]
        self.objCoord[1] = self.grid_world.deliveryCellCoord[1]
        return self.status.SUCCESS

class PlaceObject(py_trees.behaviour.Behaviour):
    def __init__(self, check_hand, name):
        self.duration = 2  # sec
        self.__start_time = None
        self.check_hand = check_hand
        super().__init__(name)

    def update(self) -> common.Status:
        if self.__start_time is None:
            self.__start_time = time.time()
            self.logger.info(f"dropping object")
            return self.status.RUNNING
        elif time.time() - self.__start_time < self.duration:
            return self.status.RUNNING
        self.__start_time = None
        self.check_hand._inHand = False
        return self.status.SUCCESS