import json
import queue
import traceback
from json import JSONDecodeError
from queue import Queue
from threading import Thread

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
    beamer_offset = (700, 2245)  # mm beamer position
    beamer_real_size = (590, 1055)  # mm beamer real size
    beamer_rotation = 270
    beamer_ppm_x = beamer_resolution[0] / beamer_real_size[0]
    beamer_ppm_y = beamer_resolution[1] / beamer_real_size[1]

    camera_resolution = (1920, 1088)
    camera_offset = (546, 2284)
    camera_real_size = (700, 1220)
    camera_rotation = 90
    camera_ppm_x = camera_resolution[1] / camera_real_size[0]
    camera_ppm_y = camera_resolution[0] / camera_real_size[1]
    # beamer upper left corner
    test_ball_1 = Ball(beamer_offset[0] + 30,
                       beamer_offset[1] + 30,
                       color=ball_color(0), ball_id=1)
    # beamer lower right corner
    test_ball_2 = Ball(beamer_offset[0] + beamer_real_size[0] - 30,
                       beamer_offset[1] + beamer_real_size[1] - 30,
                       color=ball_color(0), ball_id=2)
    # center of table
    test_ball_3 = Ball(1778 / 2, 3556 / 2, color=ball_color(0), ball_id=3)

    def __init__(self):
        self.queue_size = 1
        self.index = 0
        self.table_src = cv2.resize(cv2.imread('resources/table.jpg'), self.table_size)
        if settings.show_table:
            cv2.namedWindow('table_sim', cv2.WINDOW_NORMAL)
        self.key = 0
        self.display_q = Queue(self.queue_size)
        self.stopped = False
        self.bluetooth = BT()
        self.camera = Camera(
            resolution_x=self.camera_resolution[0],
            resolution_y=self.camera_resolution[1],
            offset_x=self.camera_offset[0],
            offset_y=self.camera_offset[1],
            ppm_x=self.camera_ppm_x,
            ppm_y=self.camera_ppm_y,
            rotation=self.camera_rotation,
            queue_size=self.queue_size
        )
        self.beamer = Beamer(
            resolution_x=self.beamer_resolution[0],
            resolution_y=self.beamer_resolution[1],
            offset_x=self.beamer_offset[0],  # mm
            offset_y=self.beamer_offset[1],  # mm
            ppm_x=self.beamer_ppm_x,
            ppm_y=self.beamer_ppm_y,
            rotation=self.beamer_rotation
        )
        self.detection = Detection(self.camera, self.beamer, self.queue_size)
        self.camera_image = self.camera.image

    def run_table_sim(self):
        t_start = now()
        # test balls:
        self.beamer.add_visual_item(self.test_ball_1)
        self.beamer.add_visual_item(self.test_ball_2)
        self.beamer.add_visual_item(self.test_ball_3)
        # debug: add spot markers
        self.beamer.add_visual_item(Cross(889, 3232, 30, ball_color(1)))  # black spot
        self.beamer.add_visual_item(Cross(889, 2667, 30, ball_color(1)))  # pink spot
        Beamer.show_image(Beamer.draw_objects(self.beamer.objects, self.beamer.outPict,
                                              self.beamer.offset_x, self.beamer.offset_y,
                                              self.beamer.ppm_x, self.beamer.ppm_y), self.beamer.rotation)
        if settings.debug and settings.show_table:
            cv2.createTrackbar('scale', 'beamer', 3, 10, nothing)
            cv2.createTrackbar('grad_val', 'beamer', Ball.grad_val, 200, nothing)
            cv2.createTrackbar('acc_thr', 'beamer', Ball.acc_thr, 200, nothing)
            cv2.createTrackbar('min_dist', 'beamer', Ball.min_dist, 300, nothing)
            cv2.createTrackbar('dp', 'beamer', Ball.dp, 15, nothing)
            cv2.createTrackbar('min_radius', 'beamer', Ball.min_radius, 70, nothing)
            cv2.createTrackbar('max_radius', 'beamer', Ball.max_radius, 150, nothing)
        # start handler threads
        t = Thread(target=self.handle_dt_message, args=())
        t.daemon = True
        t.start()
        t = Thread(target=self.handle_bt_message, args=())
        t.daemon = True
        t.start()
        while True:
            t0 = now()
            try:
                index, objects = self.display_q.get_nowait()
                self.beamer.objects = objects
            except queue.Empty:  # display queue empty
                objects = self.beamer.objects
            beamer_image = Beamer.draw_objects(objects, self.beamer.outPict,
                                               self.beamer.offset_x,
                                               self.beamer.offset_y,
                                               self.beamer.ppm_x,
                                               self.beamer.ppm_y)
            if settings.show_table:
                # show current input frame
                table_image = self.get_table_image(self.camera_image, beamer_image)
                cv2.imshow('table_sim', cv2.resize(table_image, (540, 960)))
                cv2.resizeWindow('table_sim', 540, 960)
            # show Beamer
            Beamer.show_image(beamer_image, self.beamer.rotation)
            # wait 40ms max:
            wait_time = max(200 - dt(t0, now()), 1)
            self.key = cv2.waitKey(wait_time) & 0xFF
            # wait for keypressed:
            # self.key = cv2.waitKey(0) & 0xFF
            if self.key == ord('q') or self.key == 27:
                self.stopped = True
                break
            if self.key == ord('d'):
                self.bluetooth.output_q.put(json.dumps({"what": "detect"}))
        print('Stopping after {} seconds'.format(dt(t_start, now()) / 1000))
        cv2.destroyAllWindows()
        self.stopped = True
        self.detection.stop()
        self.camera.stop()
        self.bluetooth.stop()

    def handle_dt_message(self):
        """
        Handle detection output
        """
        while True and not self.stopped:
            t0 = now()
            # process balls from detection queue
            index, image, balls = self.detection.output_q.get()
            debug('handle_dt: index: {} started'.format(index), settings.DEBUG)
            self.camera_image = image
            self.beamer.objects = balls
            json_array = {}
            for ball in balls:
                json_array[ball.ball_id] = {"x": int(ball.x), "y": int(ball.y), "v": ball_value(ball.color)}
            json_string = json.dumps({"index": index, "balls": json_array})
            debug(json_string, settings.VERBOSE)
            if self.bluetooth.is_connected:
                self.bluetooth.send(json_string)
            else:
                debug('handle_dt: index: {}: {:2d}ms'.format(index, dt(t0, now())), settings.DEBUG)

    def handle_bt_message(self):
        """
        Handle bluetooth message from App
        """
        while True and not self.stopped:
            t0 = now()
            # process message from bluetooth queue
            message = self.bluetooth.output_q.get()
            try:
                message = json.loads(message)
            except JSONDecodeError:
                print('\n' + message)
                print('json error.')
                traceback.print_exc()
                continue
            objects = []
            if message["what"] == "detect":
                self.detection.queue(self.index, self.camera.image)
                self.index += 1
                self.bluetooth.send("done")
            if message["what"] == "show":
                # noinspection PyBroadException
                try:
                    index = int(message["index"])
                    for ball_id, ball in message["balls"].items():
                        objects.append(Ball(
                            ball['x'],
                            ball['y'],
                            color=ball_color(ball['v'])))
                    if 'lines' in message:
                        for line_id, line in message["lines"].items():
                            objects.append(Line(line['x1'], line['y1'], line['x2'], line['y2']))
                    if 'ghosts' in message:
                        for ghost_id, ghost in message["ghosts"].items():
                            objects.append(Ghost(ghost['x'], ghost['y']))
                    # put objects in display queue
                    self.display_q.put([index, objects])
                    # send status 'done' to bluetooth
                    self.bluetooth.send("done")
                except BaseException:
                    traceback.print_exc()
                    index = None
                debug('handle_bt: index: {}:  {}ms'.format(index, dt(t0, now())), settings.DEBUG)

    def get_table_image(self, camera_image, beamer_image):
        table_image = np.copy(self.table_src)
        # overlay camera
        if camera_image is None:
            camera_image = np.zeros(beamer_image.shape, np.uint8)
        camera_image = cv2.resize(camera_image, self.camera_real_size)
        # make outline
        cv2.line(camera_image, (0, 0), (0, (self.camera_real_size[1])), [0, 0, 255], 5)
        cv2.line(camera_image, ((self.camera_real_size[0]), 0), ((self.camera_real_size[0]),
                                                                 (self.camera_real_size[1])),
                 [0, 0, 255], 5)
        cv2.line(camera_image, (0, 0), ((self.camera_real_size[0]), 0), [0, 0, 255], 5)
        cv2.line(camera_image, (0, (self.camera_real_size[1])), ((self.camera_real_size[0]),
                                                                 (self.camera_real_size[1])), [0, 0, 255], 5)
        # TODO: if portion of camera_image is off table_image, this fails
        lim_y = self.camera.offset_y + self.camera_real_size[1]
        lim_x = self.camera.offset_x + self.camera_real_size[0]
        lcy = min(self.camera_real_size[1], self.table_size[1] - self.camera_real_size[1])
        lcx = min(self.camera_real_size[0], self.table_size[0] - self.camera_real_size[0])
        table_image[self.camera.offset_y:lim_y, self.camera.offset_x:lim_x] = camera_image[0:lcy, 0:lcx]
        # overlay beamer
        beamer_image = cv2.resize(beamer_image, (self.beamer_real_size[0], self.beamer_real_size[1]))
        # make outline
        cv2.line(beamer_image, (0, 0), (0, (self.beamer_real_size[1])), [0, 0, 255], 5)
        cv2.line(beamer_image, ((self.beamer_real_size[0]), 0),
                 ((self.beamer_real_size[0]), (self.beamer_real_size[1])), [0, 0, 255], 5)
        cv2.line(beamer_image, (0, 0), ((self.beamer_real_size[0]), 0), [0, 0, 255], 5)
        cv2.line(beamer_image, (0, (self.beamer_real_size[1])),
                 ((self.beamer_real_size[0]), (self.beamer_real_size[1])),
                 [0, 0, 255], 5)
        # TODO: if portion of beamer_image is off table_image, this fails
        roi = table_image[
              self.beamer.offset_y:self.beamer.offset_y + int(self.beamer.resolution_y / self.beamer.ppm_y),
              self.beamer.offset_x:self.beamer.offset_x + int(self.beamer.resolution_x / self.beamer.ppm_x)]
        beamer_gray = cv2.cvtColor(beamer_image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(beamer_gray, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        table_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        beamer_fg = cv2.bitwise_and(beamer_image, beamer_image, mask=mask)
        limx = self.beamer.offset_x + int(self.beamer.resolution_x / self.beamer.ppm_x)
        limy = self.beamer.offset_y + int(self.beamer.resolution_y / self.beamer.ppm_y)
        table_image[self.beamer.offset_y:limy, self.beamer.offset_x:limx] = cv2.add(table_bg, beamer_fg)
        return table_image
