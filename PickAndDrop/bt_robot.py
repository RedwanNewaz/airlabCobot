import threading
from time import sleep
from pymycobot import MyCobot

class Robot:
    __mutex = threading.Lock()
    def __init__(self, config):
        self.setPoint = None
        self.done = False
        self._pick = False
        self.config = config

        port = self.config['COBOT']['port']
        baud = self.config['COBOT']['baudrate']
        self.mycobot = MyCobot(port, int(baud))
        self.mycobot.set_pin_mode(2, 1)
        self.mycobot.set_pin_mode(5, 1)
        self.nap_time = float(self.config['COBOT']['sleep'])

    def reset(self):
        angles = [0, 0, 0, 0, 0, 0]
        print('[+] resetting cobot')
        self.mycobot.send_angles(angles, 70)

    def dock(self):
        reset = [153.19, 137.81, -153.54, 156.79, 87.27, 13.62]
        print("::set_free_mode()\n")
        self.mycobot.send_angles(reset, 100)
        sleep(float(self.nap_time))
        self.mycobot.release_all_servos()
        print("docking success ...\n")

    def __move(self, coords):
        if (len(coords) == 2):
            coords.append(float(self.config['COBOT']['altitude']))
            # coords = [200.0, 200.0, 110.0, 0.0, -180.0, 2.51]
        coords = [coords[0], coords[1], coords[2], 0.0, -180.0, 2.51]
        self.mycobot.send_coords(coords, 70, 2)
        sleep(float(self.nap_time))

    def move(self, coords):
        if not self.__mutex.locked():
            with self.__mutex:
                # print(f"[+] moving towards {coords}")
                self.__move(coords)
                print("[+] move task completed")
                self.done = True
        else:
            # print(f"[+] moving towards {coords}")
            self.__move(coords)
            # print("[+] move task completed")
            self.done = True



    def __drop(self):

        coords = list(self.mycobot.get_coords())
        val = float(self.config['COBOT']['down'])

        coords[2] -= val  # lower down
        self.done = False
        self.move(coords)
        self.mycobot.set_basic_output(2, 1)
        self.mycobot.set_basic_output(5, 1)
        # sleep(self.nap_time)
        coords[2] += val  # going back
        self.done = False
        self.move(coords)


    def __pick(self):
        coords = list(self.mycobot.get_coords())
        val = float(self.config['COBOT']['down'])
        coords[2] -= val  # lower down
        self.done = False
        self.move(coords)
        self.mycobot.set_basic_output(2, 0)
        self.mycobot.set_basic_output(5, 0)
        sleep(float(self.nap_time))
        coords[2] += val  # going back
        self.done = False
        self.move(coords)



    def pick(self):
        if self.setPoint is None:
            print("[-] no valid pick")
            return
        with self.__mutex:
            self.__pick()
            print("[+] pick task completed")
            self._pick = True
            self.done = False



    def drop(self):
        with self.__mutex:
            self.__drop()
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