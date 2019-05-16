import cv2
import numpy as np
from queue import Queue
import queue
from .bluetooth import BT
from .beamer import Beamer


class TableSim:
    """
    A class to simulate a table to test bluetooth interaction
    """
    def __init__(self):
        self.table_src = cv2.imread('resources/table.jpg')
        self.width = self.table_src.shape[1]
        self.height = self.table_src.shape[0]
        self.table = np.copy(self.table_src)
        self.balls_on_table = []
        cv2.namedWindow('table_sim', cv2.WINDOW_NORMAL)
        self.pos = (0, 0)
        self.b_size = (40, 40)
        self.message_queue = Queue(10)
        cv2.setMouseCallback('table_sim', self.mouse_callback, None)
        self.old_pos = self.pos
        self.ball = cv2.resize(cv2.imread('resources/balls/red.png', cv2.IMREAD_UNCHANGED),
                               self.b_size, cv2.INTER_CUBIC)
        self.bluetooth = BT()
        self.beamer = Beamer()

    def run_table_sim(self):
        while True:
            # show the current table (with balls if any)
            cv2.imshow('table_sim', self.table)
            # overlay beamer TODO
            # image = self.beamer.get_image()
            # print(image)
            # get (nonblocking) bluetooth read
            msg = self.bluetooth.read()
            if msg is not None:
                self.handle_bt_message(msg)
            # get nonblocking 'detection read'
            # TODO: outside of table_sim this will be detection.read()
            try:
                msg = self.message_queue.get(timeout=0.04)
            except queue.Empty:
                msg = None
            # if there is an input (from mouse_callback), send it to app
            if msg is not None:
                self.bluetooth.send('{}'.format(msg))
            key = cv2.waitKey(40) & 0xFF
            if key == ord('q') or key == 27:
                break
        cv2.destroyAllWindows()

    def start(self):
        self.run_table_sim()

    def update_table(self) -> None:
        """
        Renew the table bitmap from src and overlay all balls_on_table
        """
        self.table = np.copy(self.table_src)
        for pos in self.balls_on_table:
            n = 0
            ball = self.ball
            for rows in ball:
                n += 1
                m = 0
                for pix in rows:
                    x = m + pos[1]
                    y = n + pos[0]
                    if x < self.width and y < self.height:
                        self.table[y, x, :] = self.table[y, x, :] * (1 - pix[3] // 255) + pix[:3] * (pix[3] // 255)
                    m += 1

    def mouse_callback(self, event, x, y, flags, param):
        # print('flags: {} param: {}'.format(flags, param))
        if event == cv2.EVENT_LBUTTONDOWN:
            # TODO: check if ball at click position (for moving)
            # else create ball here
            self.balls_on_table.append((y - self.b_size[0] // 2, x - self.b_size[1] // 2))
            self.update_table()
            # send to message_queue (simulating detection.read)
            # calculate table pos from pixel:
            x, y = self.real_pos(x, y)
            self.message_queue.put('b{}'.format((x, y)))
        elif event == cv2.EVENT_LBUTTONUP:
            pass
        elif event == cv2.EVENT_RBUTTONDOWN:
            pass

    def handle_bt_message(self, message) -> None:
        """
        Process a message read from bluetooth class
        :param message: the message read by the bluetooth class
        :return: None
        """
        # print("bt_message = " + message)
        # first character of message is 'what'
        if message[0] == 'n':
            print('ballName = ' + message[message.find("(")+1:message.find(")")])
        elif message[0] == 'b':
            # split (x, y) into variables
            message = message[message.find("(")+1:message.find(")")]
            x, y = message.split(',')
            x = float(x)
            y = float(y)
            # create ball at screen_pos(x, y)
            print("x={} y={}".format(x, y))
            self.balls_on_table.append(self.screen_pos(y - self.b_size[0] // 2, x - self.b_size[1] // 2))
            self.update_table()

    @staticmethod
    def screen_pos(x, y):
        """
        Function for conversion of real mm and screen pix
        :param x: realX
        :param y: realY
        :return: screenx, screeny
        """
        w = 1778
        h = 3556
        x0 = 100
        x1 = 1000
        y0 = 100
        y1 = 1860
        return int(x / w * (x1 - x0) + x0), int(y / h * (y1 - y0) + y0)

    @staticmethod
    def real_pos(x, y):
        """
        Function for conversion of real mm and screen pix
        :param x: screenX
        :param y: screenY
        :return: realx, realy
        """
        # top left
        # x0, y0 = 100, 100
        # top right
        # x1, y1 = 1000, 100
        # bottom right
        # x3, y3 = 1000, 1860
        w = 1778
        h = 3556
        x0 = 100
        x1 = 1000
        y0 = 100
        y1 = 1860
        return min(max((x - x0), 0) / (x1 - x0), 1) * w,  min(max((y - y0), 0) / (y1 - y0), 1) * h
