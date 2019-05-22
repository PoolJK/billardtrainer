import json
from json import JSONDecodeError
from queue import Queue
import queue

from .bluetooth import BT
from .beamer import Beamer
from .visual_items.ball import Ball
from .visual_items.line import Line
from .utils import *


class TableSim:
    """
    A class to simulate a table to test bluetooth interaction
    """

    # test values for beamer position
    # beamer_position = (360, 1200)  # pixel
    # beamer_size = (366, 651)  # pixel
    t_size = (1080, 2160)  # pixel table size
    ppm = 1080 / 1778  # table sim ppm
    b_pos = (380 / ppm, 1460 / ppm)  # mm beamer position
    b_res = (720, 1280)  # pixel beamer resolution
    real_size = (540, 960)  # mm beamer real size
    ppmx = b_res[0] / real_size[0]
    ppmy = b_res[1] / real_size[1]
    b1 = Ball(b_pos[0] + 30,
              b_pos[1] + 30,
              color=ball_color(0))
    b2 = Ball(b_pos[0] + real_size[0] - 30,
              b_pos[1] + real_size[1] - 30,
              color=ball_color(0))
    b3 = Ball(1778 / 2, 3556 / 2, color=ball_color(0))

    def __init__(self):
        self.table_src = cv2.imread('resources/table.jpg')
        self.width = self.table_src.shape[1]
        self.height = self.table_src.shape[0]
        print('w={} h={}'.format(self.width, self.height))
        self.table = np.copy(self.table_src)
        self.balls_on_table = []
        cv2.namedWindow('table_sim', cv2.WINDOW_NORMAL)
        self.b_size = (40, 40)
        self.message_queue = Queue(10)
        cv2.setMouseCallback('table_sim', self.mouse_callback, None)
        self.bluetooth = BT()
        self.beamer = Beamer(
            resolution_x=self.b_res[0],
            resolution_y=self.b_res[1],
            offset_x=self.b_pos[0],  # mm
            offset_y=self.b_pos[1],  # mm
            ppm_x=self.ppmx,
            ppm_y=self.ppmy)
        # self.beamer.hide()

    def run_table_sim(self):
        # test balls:
        self.beamer.add_visual_item(self.b1)
        self.beamer.add_visual_item(self.b2)
        self.beamer.add_visual_item(self.b3)
        self.beamer.show_objects()
        # self.beamer.hide()
        # main loop as fps loop
        cv2.imshow('table_sim', self.overlay_beamer_image())
        cv2.resizeWindow('table_sim', 540, 960)
        while True:
            t0 = now()
            # show the current table (with balls if any)
            # get (nonblocking) bluetooth read
            msg = self.bluetooth.read()
            if msg is not None:
                # for writing beamer, act as if inputs from bluetooth are detection inputs
                self.handle_dt_message(msg)
                # self.handle_bt_message(msg)
            # get nonblocking 'detection read'
            # msg = self.fake_detection_read()
            # if msg is not None:
            #     self.handle_dt_message(msg)
            d = dt(t0, now())
            print('loop time: {: 4d}ms'.format(d), end='\r')
            key = cv2.waitKey(max(40, 100 - d)) & 0xFF
            if key == ord('q') or key == 27:
                break
        cv2.destroyAllWindows()

    def start(self):
        self.run_table_sim()

    def mouse_callback(self, event, x, y, flags, param):
        # print('flags: {} param: {}'.format(flags, param))
        if flags:
            print('flags={}'.format(flags))
        if param:
            print('param={}'.format(param))
        if event == cv2.EVENT_LBUTTONDOWN:
            # TODO: check if ball at click position (for moving)
            pass
        elif event == cv2.EVENT_LBUTTONUP:
            pass
        elif event == cv2.EVENT_RBUTTONDOWN:
            # TODO: else create ball here
            # send to message_queue (simulating detection.read)
            # calculate table pos from pixel:
            x, y = self.real_pos(x, y)
            self.message_queue.put('b{}'.format((x, y)))

    def fake_detection_read(self):
        # TODO: outside of table_sim this will be detection.read()
        try:
            msg = self.message_queue.get_nowait()
            print('detection msg read: {}'.format(msg))
        except queue.Empty:
            msg = None
        return msg

    def overlay_beamer_image(self):
        table_image = np.copy(self.table_src)
        b_y = int(self.b_pos[1] * self.ppm)  # beamer in table_image
        b_x = int(self.b_pos[0] * self.ppm)
        r_w = self.real_size[0]  # beamer in real
        r_h = self.real_size[1]
        i_w = int(r_w * self.ppm)  # beamer in table_image
        i_h = int(r_h * self.ppm)
        beamer_image = cv2.resize(self.beamer.get_image(),
                                  (int(i_w), int(i_h))
                                  )
        # make outline
        beamer_image[:, 0:2] = (0, 0, 255)
        beamer_image[:, i_w - 3:i_w - 1] = (0, 0, 255)
        beamer_image[0:2, :] = (0, 0, 255)
        beamer_image[i_h - 3:i_h - 1, :] = (0, 0, 255)
        # TODO: if portion of beamer_image is off table_image, this fails
        roi = table_image[b_y:b_y + i_h, b_x:b_x + i_w]
        beamer_gray = cv2.cvtColor(beamer_image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(beamer_gray, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        table_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        beamer_fg = cv2.bitwise_and(beamer_image, beamer_image, mask=mask)
        table_image[b_y:b_y + i_h, b_x:b_x + i_w] = cv2.add(table_bg, beamer_fg)
        # cv2.imshow('res', img1)
        return table_image

    def handle_dt_message(self, message):
        # if there is an input (from mouse_callback), send it to app
        # self.bluetooth.send('{}'.format(message))
        # writing beamer class: add balls to beamer
        try:
            message = json.loads(message)
        except JSONDecodeError as e:
            print('\njson error.')
            print(message)
            raise e
        self.beamer.clear_image()
        res = ""
        for ball_id, ball in message["balls"].items():
            res += 'id={} x={}, y={}, v={}'.format(ball_id, ball['x'], ball['y'], ball['v'])
            self.beamer.add_visual_item(Ball(
                ball['x'],
                ball['y'],
                color=ball_color(ball['v'])))
        if 'lines' in message:
            for line in message["lines"].items():
                self.beamer.add_visual_item(Line(line['x1'], line['y1'], line['x2'], line['y2']))
        self.beamer.show_objects()
        self.beamer.resize_window()
        # self.beamer.hide()
        self.bluetooth.send("done")
        cv2.imshow('table_sim', self.overlay_beamer_image())
        cv2.resizeWindow('table_sim', 540, 960)
        # self.bluetooth.send(res)

    def handle_bt_message(self, message):
        """
        Process a message read from bluetooth class
        :param message: the message read by the bluetooth class
        """
        # print("bt_message = " + message)
        # first character of message is 'what'
        if message[0] == 'n':
            print('ballName = ' + message[message.find("(") + 1:message.find(")")])
        elif message[0] == 'b':
            # split (x, y) into variables
            message = message[message.find("(") + 1:message.find(")")]
            x, y = message.split(',')
            x = float(x)
            y = float(y)
            # create ball at screen_pos(x, y)
            print("x={} y={}".format(x, y))
            self.balls_on_table.append(self.screen_pos(y - self.b_size[0] // 2, x - self.b_size[1] // 2))

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
        return min(max((x - x0), 0) / (x1 - x0), 1) * w, min(max((y - y0), 0) / (y1 - y0), 1) * h
