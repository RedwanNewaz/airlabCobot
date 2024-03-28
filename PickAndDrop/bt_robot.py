from pymycobot import MyCobot
import time
class BTRobot:
    def __init__(self, config):
        self.config = config
        port = self.config['COBOT']['port']

        self.mycobot = MyCobot(port, 115200)
        self.mycobot.set_pin_mode(2, 1)
        self.mycobot.set_pin_mode(5, 1)

    def move(self, coords):
        if (len(coords) == 2):
            coords.append(float(self.config['COBOT']['altitude']))
        # coords = [200.0, 200.0, 110.0, 0.0, -180.0, 2.51]
        coords = [coords[0], coords[1], coords[2], 0.0, -180.0, 2.51]
        self.mycobot.send_coords(coords, 70, 2)
        print("::send_coords() ==> send coords {}, speed 70, mode 0\n".format(coords))

    @property
    def getCoords(self):
        coords = list(self.mycobot.get_coords())
        return coords[:2]
    def reset(self):
        angles = [0, 0, 0, 0, 0, 0]
        print('[+] resetting cobot')
        self.mycobot.send_angles(angles, 70)

    def dock(self):
        reset = [153.19, 137.81, -153.54, 156.79, 87.27, 13.62]
        print("::set_free_mode()\n")
        self.mycobot.send_angles(reset, 100)
        time.sleep(float(self.config['COBOT']['sleep']))
        self.mycobot.release_all_servos()
        print("docking success ...\n")

    def pick(self):
        # read this parameter from config file
        coords = list(self.mycobot.get_coords())
        print(f'current coord {coords}')
        val = float(self.config['COBOT']['down'])
        coords[2] -= val  # lower down
        print(f'desire coord {coords}')
        # self.move(coords)
        self.mycobot.set_basic_output(2, 0)
        self.mycobot.set_basic_output(5, 0)
        time.sleep(float(self.config['COBOT']['sleep']))
        coords[2] += val  # going back
        # self.move(coords)

    def drop(self):
        coords = list(self.mycobot.get_coords())
        print(f'current coord {coords}')
        val = 100
        coords[2] -= val  # lower down
        print(f'desire coord {coords}')
        # self.move(coords)
        time.sleep(float(self.config['COBOT']['sleep']))
        self.mycobot.set_basic_output(2, 1)
        self.mycobot.set_basic_output(5, 1)
        coords[2] += val  # going back
        # self.move(coords)