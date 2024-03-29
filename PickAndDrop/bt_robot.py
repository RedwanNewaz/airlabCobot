import threading
from time import sleep
class Robot:
    __mutex = threading.Lock()
    def __init__(self):
        self.setPoint = None
        self.done = False
        self._pick = False

    def move(self, coords):
        if not self.__mutex.locked():
            with self.__mutex:
                # print(f"[+] moving towards {coords}")
                sleep(1)
                print("[+] move task completed")
                self.done = True
        else:
            # print(f"[+] moving towards {coords}")
            sleep(1)
            # print("[+] move task completed")
            self.done = True



    def pick(self):
        #TODO read this parameter from config file
        # FIXME replace with coords = list(self.mycobot.get_coords())
        if self.setPoint is None:
            print("[-] no valid pick")
            return
        with self.__mutex:
            self.done = False
            coords = self.setPoint.copy()
            coords.append(100)
            val = 10
            coords[2] -= val  # going back
            self.move(coords)
            # await asyncio.sleep(1)
            sleep(1)
            self.done = False
            coords[2] += val  # going back
            self.move(coords)
            print("[+] pick task completed")
            self._pick = True
            self.done = False



    def drop(self):
        # TODO read this parameter from config file
        # FIXME replace with coords = list(self.mycobot.get_coords())
        with self.__mutex:
            coords = self.setPoint.copy()
            coords.append(100)
            val = 10
            coords[2] -= val  # going back
            self.move(coords)
            # await asyncio.sleep(1)
            sleep(1)
            self.done = False
            coords[2] += val  # going back
            self.move(coords)
            print("[+] drop task completed")
            self._pick = False


    def task_move(self):
        if self.__mutex.locked():
            # print('[-] task move cannot be created ..')
            return False
        thread_move = threading.Thread(target=self.move, args=(self.setPoint,))
        thread_move.start()
        return True
    def task_pick(self):
        if self.__mutex.locked():
            # print('[-] task pick cannot be created ..')
            return False
        thread_pick = threading.Thread(target=self.pick)
        thread_pick.start()
        return True
    def task_drop(self):
        if self.__mutex.locked():
            # print('[-] task drop cannot be created ..')
            return False
        thread_drop = threading.Thread(target=self.drop)
        thread_drop.start()
        return True