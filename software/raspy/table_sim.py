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

    test_ball_1 = Ball(beamer_offset[0] + 30,
                       beamer_offset[1] + 30,
                       color=ball_color(0))
    test_ball_2 = Ball(beamer_offset[0] + beamer_real_size[0] - 30,
                       beamer_offset[1] + beamer_real_size[1] - 30,
                       color=ball_color(0))
    test_ball_3 = Ball(1778 / 2, 3556 / 2, color=ball_color(0), text='blue')

    def __init__(self):
        self.table_src = cv2.resize(cv2.imread('resources/table.jpg'), self.table_size)
        if not settings.on_pi or settings.debug:
            cv2.namedWindow('table_sim', cv2.WINDOW_NORMAL)
            cv2.setMouseCallback('table_sim', self.mouse_callback, None)
        self.key = 0
        self.display_q = Queue(10)
        self.bluetooth = BT()
        self.camera = Camera(
            resolution_x=self.camera_resolution[0],
            resolution_y=self.camera_resolution[1],
            offset_x=self.camera_offset[0],
            offset_y=self.camera_offset[1],
            ppm_x=self.camera_ppm_x,
            ppm_y=self.camera_ppm_y,
            rotation=self.camera_rotation
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
        self.frames = {i: "" for i in range(10)}
        self.detection = Detection(self.camera, self.beamer, Queue(10))

    def run_table_sim(self):
        # test balls:
        self.beamer.add_visual_item(self.test_ball_1)  # @beamer(0,0)
        self.beamer.add_visual_item(self.test_ball_2)  # @beamer(w,h)
        self.beamer.add_visual_item(self.test_ball_3)  # @tablecenter
        # debug: add spot markers
        self.beamer.add_visual_item(Cross(889, 3232, 30, ball_color(1)))  # black spot
        self.beamer.add_visual_item(Cross(889, 2667, 30, ball_color(1)))  # pink spot
        self.beamer.draw_objects(self.beamer.objects, self.beamer.outPict,
                                 self.beamer.offset_x, self.beamer.offset_y,
                                 self.beamer.ppm_x, self.beamer.ppm_y)
        # self.beamer.hide()
        if settings.debug:
            cv2.createTrackbar('grad_val', 'beamer', Ball.grad_val, 200, nothing)
            cv2.createTrackbar('acc_thr', 'beamer', Ball.acc_thr, 200, nothing)
            cv2.createTrackbar('min_dist', 'beamer', Ball.min_dist, 300, nothing)
            cv2.createTrackbar('dp', 'beamer', Ball.dp, 15, nothing)
            cv2.createTrackbar('min_radius', 'beamer', Ball.min_radius, 70, nothing)
            cv2.createTrackbar('max_radius', 'beamer', Ball.max_radius, 150, nothing)
        # main loop as fps loop
        while True:
            t0 = now()
            cam_q = self.camera.output_q.qsize()
            det_q = self.detection.output_q.qsize()
            bt_q = self.bluetooth.output_q.qsize()
            disp_q = self.display_q.qsize()

            try:
                index, beamer_image = self.display_q.get_nowait()
                if settings.show_table:
                    self.show_table(index, self.frames[index], beamer_image)
                else:
                    Beamer.show_image(beamer_image, self.beamer.rotation)
                self.frames[index] = ""
                continue
            except queue.Empty:
                pass
            try:
                objects = self.bluetooth.output_q.get_nowait()
                t = Thread(target=self.handle_bt_message, args=[objects])
                t.daemon = True
                t.start()
                continue
            except queue.Empty:
                pass
            try:
                index, balls = self.detection.output_q.get_nowait()
                t = Thread(target=self.handle_dt_message, args=[index, balls])
                t.daemon = True
                t.start()
                continue
            except queue.Empty:
                pass
            i = 0
            while i < 10:
                if self.frames[i] is "":
                    break
                i += 1
            if i < 10:
                try:
                    self.frames[i] = self.camera.output_q.get_nowait()
                    if self.frames[i] is 0:
                        print('wtf')
                        wait(10000)
                    else:
                        self.detection.queue(i, self.frames[i])
                except queue.Empty:
                    pass
            main_loop = dt(t0, now())
            # if main_loop > 0:
            n = 0
            for i in range(10):
                if self.frames[i] is not '':
                    n += 1
            debug('{}frames: {}   cam_q: {}   det_q: {}   bt_q: {}   disp_q: {}'.format(
                'loop: {:2d}ms'.format(main_loop) if settings.debug_level >= settings.TIMING else '',
                n, cam_q, det_q, bt_q, disp_q), settings.DEBUG)
            # wait 40ms max:
            self.key = cv2.waitKey(max(40 - main_loop, 1)) & 0xFF
            # wait for keypressed:
            # self.key = cv2.waitKey(0) & 0xFF
            if self.key == ord('q') or self.key == 27:
                break
        cv2.destroyAllWindows()
        self.bluetooth.stop()

    def handle_dt_message(self, index, balls):
        t0 = now()
        debug('handle_dt_message', settings.VERBOSE)
        json_array = {}
        ball_id = 0
        for ball in balls:
            json_array[ball_id] = {"x": int(ball.x), "y": int(ball.y), "v": ball_value(ball.color)}
            ball_id += 1
        json_string = json.dumps({"index": index, "balls": json_array})
        debug(json_string, settings.VERBOSE)
        if settings.simulate:
            self.bluetooth.output_q.put(json_string)
        else:
            self.bluetooth.send(json_string)
        debug('handle_dt: {:2d}ms'.format(dt(t0, now())), settings.TIMING)

    def handle_bt_message(self, objects):
        t0 = now()
        debug('handle_bt_message: \"{}\"'.format(objects), settings.VERBOSE)
        self.beamer.clear_objects()
        try:
            message = json.loads(objects)
        except JSONDecodeError:
            print('\n' + objects)
            print('json error.')
            traceback.print_exc()
            return
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
        self.beamer.draw_objects(self.beamer.objects, self.beamer.outPict,
                                 self.beamer.offset_x, self.beamer.offset_y,
                                 self.beamer.ppm_x, self.beamer.ppm_y)
        index = message["index"]
        self.display_q.put([index, self.beamer.get_image()])
        debug('handle_bt: index: {}:  {}ms'.format(index, dt(t0, now())), settings.DEBUG)
        self.bluetooth.send(json.dumps({index: 1}))

    def show_table(self, index, camera_image, beamer_image):
        t0 = now()
        cv2.imshow('table_sim', self.overlay_beamer(beamer_image, self.overlay_camera(camera_image, self.table_src)))
        Beamer.show_image(beamer_image, self.beamer.rotation)
        cv2.resizeWindow('table_sim', 540, 960)
        debug('show_table: index: {}:  {:3d}ms'.format(index, dt(t0, now())), settings.DEBUG)

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

    def overlay_camera(self, camera_image, table_image):
        camera_image = cv2.resize(camera_image, self.camera_real_size)
        # make outline
        cv2.line(camera_image, (0, 0), (0, (self.camera_real_size[1])), [0, 0, 255], 5)
        cv2.line(camera_image, ((self.camera_real_size[0]), 0), ((self.camera_real_size[0]),
                                                                 (self.camera_real_size[1])),
                 [0, 0, 255], 5)
        cv2.line(camera_image, (0, 0), ((self.camera_real_size[0]), 0), [0, 0, 255], 5)
        cv2.line(camera_image, (0, (self.camera_real_size[1])), ((self.camera_real_size[0]),
                                                                 (self.camera_real_size[1])), [0, 0, 255], 5)
        # camera_image = rotate(camera_image, -self.camera_rotation)
        # TODO: if portion of camera_image is off table_image, this fails
        lim_y = self.camera.offset_y + self.camera_real_size[1]
        lim_x = self.camera.offset_x + self.camera_real_size[0]
        lcy = min(self.camera_real_size[1], self.table_size[1] - self.camera_real_size[1])
        lcx = min(self.camera_real_size[0], self.table_size[0] - self.camera_real_size[0])
        table_image[self.camera.offset_y:lim_y, self.camera.offset_x:lim_x] = camera_image[0:lcy, 0:lcx]
        return table_image

    def overlay_beamer(self, beamer_image, table_with_cam):
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
        roi = table_with_cam[
              self.beamer.offset_y:self.beamer.offset_y + int(self.beamer.resolution_y / self.beamer.ppm_y),
              self.beamer.offset_x:self.beamer.offset_x + int(self.beamer.resolution_x / self.beamer.ppm_x)]
        beamer_gray = cv2.cvtColor(beamer_image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(beamer_gray, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        table_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        beamer_fg = cv2.bitwise_and(beamer_image, beamer_image, mask=mask)
        table_with_cam[
        self.beamer.offset_y:self.beamer.offset_y + int(self.beamer.resolution_y / self.beamer.ppm_y),
        self.beamer.offset_x:self.beamer.offset_x + int(self.beamer.resolution_x / self.beamer.ppm_x)] \
            = cv2.add(table_bg, beamer_fg)
        return table_with_cam
        # for roi only overlayed parts:
        # [
        #        min(self.beamer.offset_y, self.camera.offset_y):max(self.beamer.offset_y + self.beamer_real_size[1],
        #                                                            self.camera.offset_y + self.camera_real_size[1]),
        #        min(self.beamer.offset_x, self.camera.offset_x):max(self.beamer.offset_x + self.beamer_real_size[0],
        #                                                            self.camera.offset_x + self.camera_real_size[1]), :]
