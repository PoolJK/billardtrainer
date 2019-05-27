import json
from json import JSONDecodeError
from queue import Queue

from .classes import settings
from .classes.bluetooth import BT
from .classes.camera import Camera
from .classes.beamer import Beamer
from .classes.detection import Detection
from .classes.visual_items import *
from .classes.ball import Ball
from .classes.utils import *


class TableSim:
    """
    A class to simulate a table to test bluetooth interaction
    """

    # test values for beamer position
    table_size = (1778, 3556)  # pixel table size

    beamer_resolution = (1080, 1920)  # pixel beamer resolution
    beamer_offset = (700, 2265)  # mm beamer position
    beamer_real_size = (590, 1055)  # mm beamer real size
    beamer_rotation = 270
    beamer_ppm_x = beamer_resolution[0] / beamer_real_size[0]
    beamer_ppm_y = beamer_resolution[1] / beamer_real_size[1]

    camera_resolution = (1088, 1920)
    camera_offset = (543, 2293)
    camera_real_size = (711, 1220)
    camera_rotation = 90
    camera_ppm_x = camera_resolution[0] / camera_real_size[0]
    camera_ppm_y = camera_resolution[1] / camera_real_size[1]

    test_ball_1 = Ball(beamer_offset[0] + 30,
                       beamer_offset[1] + 30,
                       color=ball_color(0))
    test_ball_2 = Ball(beamer_offset[0] + beamer_real_size[0] - 30,
                       beamer_offset[1] + beamer_real_size[1] - 30,
                       color=ball_color(0))
    test_ball_3 = Ball(1778 / 2, 3556 / 2, color=ball_color(0), text='blue')

    def __init__(self):
        self.table_src = cv2.resize(cv2.imread('resources/table.jpg'), self.table_size)
        cv2.namedWindow('table_sim', cv2.WINDOW_NORMAL)
        self.message_queue = Queue(10)
        cv2.setMouseCallback('table_sim', self.mouse_callback, None)
        self.key = 0
        self.bluetooth = BT()
        self.camera = Camera(
            resolution_x=self.camera_resolution[0],
            resolution_y=self.camera_resolution[1],
            offset_x=self.camera_offset[0],
            offset_y=self.camera_offset[1],
            ppm_x=self.camera_ppm_x,
            ppm_y=self.camera_ppm_y
        )
        self.beamer = Beamer(
            resolution_x=self.beamer_resolution[0],
            resolution_y=self.beamer_resolution[1],
            offset_x=self.beamer_offset[0],  # mm
            offset_y=self.beamer_offset[1],  # mm
            ppm_x=self.beamer_ppm_x,
            ppm_y=self.beamer_ppm_y)
        self.detection = Detection(self.camera)

    def run_table_sim(self):
        # test balls:
        self.beamer.add_visual_item(self.test_ball_1)  # @beamer(0,0)
        self.beamer.add_visual_item(self.test_ball_2)  # @beamer(w,h)
        self.beamer.add_visual_item(self.test_ball_3)  # @tablecenter
        # debug: add spot markers
        self.beamer.add_visual_item(Cross(889, 3232, 30, ball_color(1)))  # black spot
        self.beamer.add_visual_item(Cross(889, 2667, 30, ball_color(1)))  # pink spot
        self.beamer.show_visual_items()
        # self.beamer.hide()
        if not settings.on_pi:
            cv2.createTrackbar('grad_val', 'beamer', Ball.grad_val, 100, nothing)
            cv2.createTrackbar('acc_thr', 'beamer', Ball.acc_thr, 200, nothing)
            cv2.createTrackbar('min_dist', 'beamer', Ball.min_dist, 300, nothing)
            cv2.createTrackbar('dp', 'beamer', Ball.dp, 15, nothing)
            cv2.createTrackbar('min_radius', 'beamer', Ball.min_radius, 70, nothing)
            cv2.createTrackbar('max_radius', 'beamer', Ball.max_radius, 150, nothing)
        # main loop as fps loop
        print('starting detection')
        self.detection.start()
        while True:
            t0 = now()
            self.show_table()
            # show the current table (with balls if any)
            # get (nonblocking) bluetooth read
            msg = self.bluetooth.read()
            if msg is not None:
                # for writing beamer, act as if inputs from bluetooth are detection inputs
                # self.handle_dt_message(msg)
                self.handle_bt_message(msg)
            # get nonblocking 'detection read'
            msg = self.detection.read()
            if msg is not None:
                self.handle_dt_message(msg)
            d = dt(t0, now())
            if settings.debug:
                print('main loop time: {:3d}ms (waiting time: {}'.format(d, max(40 - d, 1)))
            # wait 40ms max:
            self.key = cv2.waitKey(max(40 - d, 1)) & 0xFF
            # wait for keypressed:
            # self.key = cv2.waitKey(0) & 0xFF
            if self.key == ord('q') or self.key == 27:
                break
            elif self.key == ord('p'):
                self.detection.pause(5000)
        cv2.destroyAllWindows()

    def handle_dt_message(self, message):
        if settings.debug:
            print('handle_dt_message\n', end='')
        self.beamer.clear_image()
        for ball in message:
            self.beamer.add_visual_item(ball)
        self.beamer.show_visual_items()

    # if there is an input (from mouse_callback), send it to app
    # self.bluetooth.send('{}'.format(message))
    # self.bluetooth.send(res)

    def handle_bt_message(self, message):
        if settings.debug:
            print('handle_bt_message')
        # writing beamer class: add balls to beamer
        try:
            message = json.loads(message)
        except JSONDecodeError:
            print('\n' + message)
            print('json error.')
            exit(0)
        self.beamer.clear_image()
        for ball_id, ball in message["balls"].items():
            self.beamer.add_visual_item(Ball(
                ball['x'],
                ball['y'],
                color=ball_color(ball['v'])))
        if 'lines' in message:
            for line_id, line in message["lines"].items():
                self.beamer.add_visual_item(Line(line['x1'], line['y1'], line['x2'], line['y2']))
        if 'ghosts' in message:
            for ghost_id, ghost in message["ghosts"].items():
                self.beamer.add_visual_item(Ghost(ghost['x'], ghost['y']))
        self.beamer.show_visual_items()
        # self.beamer.resize_window()
        # self.beamer.hide()
        self.show_table()
        self.detection.pause(5000)
        self.bluetooth.send("done")

    def show_table(self):
        cv2.imshow('table_sim', self.overlay_beamer(self.overlay_camera(self.table_src)))
        cv2.resizeWindow('table_sim', 540, 960)

    @staticmethod
    def mouse_callback(event, x, y, flags, param):
        # print('flags: {} param: {}'.format(flags, param))
        if flags or param or x or y:
            pass
        if event == cv2.EVENT_LBUTTONDOWN:
            # TODO: check if ball at click position (for moving)
            pass
        elif event == cv2.EVENT_LBUTTONUP:
            pass
        elif event == cv2.EVENT_RBUTTONDOWN:
            # TODO: else create ball here
            # send to message_queue (simulating detection.read)
            # calculate table pos from pixel:
            pass

    def overlay_camera(self, table_image):
        # camera
        b_x = int(self.camera_offset[0])  # camera in table_image
        b_y = int(self.camera_offset[1])
        r_w = self.camera_real_size[0]  # camera in real
        r_h = self.camera_real_size[1]
        i_w = int(r_w)  # camera in table_image
        i_h = int(r_h)
        camera_image = cv2.resize(self.camera.get_image(),
                                  (i_w, i_h))
        # make outline
        cv2.line(camera_image, (0, 0), (0, i_h), [0, 0, 255], 5)
        cv2.line(camera_image, (i_w, 0), (i_w, i_h), [0, 0, 255], 5)
        cv2.line(camera_image, (0, 0), (i_w, 0), [0, 0, 255], 5)
        cv2.line(camera_image, (0, i_h), (i_w, i_h), [0, 0, 255], 5)
        # camera_image = rotate(camera_image, -self.camera_rotation)
        # TODO: if portion of camera_image is off table_image, this fails
        lim_y = b_y + i_h
        lim_x = b_x + i_w
        lcy = min(i_h, self.table_size[1] - b_y)
        lcx = min(i_w, self.table_size[0] - b_x)
        table_image[b_y:lim_y, b_x:lim_x] = camera_image[0:lcy, 0:lcx]
        return table_image

    def overlay_beamer(self, table_image):
        # beamer
        b_x = int(self.beamer_offset[0])  # beamer in table_image
        b_y = int(self.beamer_offset[1])
        r_w = self.beamer_real_size[0]  # beamer in real
        r_h = self.beamer_real_size[1]
        i_w = int(r_w)  # beamer in table_image
        i_h = int(r_h)
        beamer_image = cv2.resize(self.beamer.get_image(),
                                  (int(i_w), int(i_h)))
        # make outline
        cv2.line(beamer_image, (0, 0), (0, i_h), [0, 0, 255], 5)
        cv2.line(beamer_image, (i_w, 0), (i_w, i_h), [0, 0, 255], 5)
        cv2.line(beamer_image, (0, 0), (i_w, 0), [0, 0, 255], 5)
        cv2.line(beamer_image, (0, i_h), (i_w, i_h), [0, 0, 255], 5)
        # TODO: if portion of beamer_image is off table_image, this fails
        roi = table_image[b_y:b_y + i_h, b_x:b_x + i_w]
        beamer_gray = cv2.cvtColor(beamer_image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(beamer_gray, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        table_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        beamer_fg = cv2.bitwise_and(beamer_image, beamer_image, mask=mask)
        table_image[b_y:b_y + i_h, b_x:b_x + i_w] = cv2.add(table_bg, beamer_fg)
        return table_image
