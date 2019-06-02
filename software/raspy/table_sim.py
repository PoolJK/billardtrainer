import json
import queue
import statistics
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
                       color=ball_color(0))
    # beamer lower right corner
    test_ball_2 = Ball(beamer_offset[0] + beamer_real_size[0] - 30,
                       beamer_offset[1] + beamer_real_size[1] - 30,
                       color=ball_color(0))
    # center of table
    test_ball_3 = Ball(1778 / 2, 3556 / 2, color=ball_color(0), text='blue')

    def __init__(self):
        self.queue_size = 5
        self.table_src = cv2.resize(cv2.imread('resources/table.jpg'), self.table_size)
        if settings.show_table:
            cv2.namedWindow('table_sim', cv2.WINDOW_NORMAL)
            cv2.setMouseCallback('table_sim', self.mouse_callback, None)
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
        self.input_frames = {i: "" for i in range(self.queue_size)}
        self.output_frames = {i: "" for i in range(self.queue_size)}
        self.detection = Detection(self.camera, self.beamer, self.queue_size)
        self.measured_fps = []
        self.t_last_fps = now()
        self.fps = 0
        self.lock = Lock()

    def manage_input(self):
        index = 0
        while True and not self.stopped:
            # if the frame array is not full, read a frame into it and start detection on it
            self.lock.acquire()
            if self.input_frames[index] is '':
                try:
                    self.input_frames[index] = self.camera.output_q.get_nowait()
                    self.detection.queue(index, self.input_frames[index])
                    self.lock.release()
                except queue.Empty:  # camera queue empty
                    self.lock.release()
                    continue
            else:
                self.lock.release()
            # go to next index, or 0 if queue_size
            index += 1
            if index == self.queue_size:
                index = 0

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
        if settings.debug:
            cv2.createTrackbar('scale', 'beamer', 3, 10, nothing)
            cv2.createTrackbar('grad_val', 'beamer', Ball.grad_val, 200, nothing)
            cv2.createTrackbar('acc_thr', 'beamer', Ball.acc_thr, 200, nothing)
            cv2.createTrackbar('min_dist', 'beamer', Ball.min_dist, 300, nothing)
            cv2.createTrackbar('dp', 'beamer', Ball.dp, 15, nothing)
            cv2.createTrackbar('min_radius', 'beamer', Ball.min_radius, 70, nothing)
            cv2.createTrackbar('max_radius', 'beamer', Ball.max_radius, 150, nothing)
        # start threads
        t = Thread(target=self.handle_dt_message, args=())
        t.daemon = True
        t.start()
        t = Thread(target=self.handle_bt_message, args=())
        t.daemon = True
        t.start()
        t = Thread(target=self.display, args=())
        t.daemon = True
        t.start()
        t = Thread(target=self.manage_input, args=())
        t.daemon = True
        t.start()
        # main loop as fps display loop
        index = 0
        while True and dt(t_start, now()) < 60000:
            t0 = now()
            self.lock.acquire()
            while self.output_frames[index] is '':
                self.lock.release()
                debug("main_loop: output_frames[{}] is \'\'".format(index), settings.DEBUG)
                wait(20)
                self.lock.acquire()
            table_image, beamer_image = self.output_frames[index]
            # count number of non-empty frames
            in_frames = out_frames = '['
            for i in range(self.queue_size):
                if self.input_frames[i] is not '':
                    in_frames += '{},'.format(i)
                if self.output_frames[i] is not '':
                    out_frames += '{},'.format(i)
            in_frames += ']'
            out_frames += ']'
            self.output_frames[index] = ''
            self.lock.release()
            # queue sizes
            cam_q = self.camera.output_q.qsize()
            det_q = self.detection.output_q.qsize()
            bt_q = self.bluetooth.output_q.qsize()
            disp_q = self.display_q.qsize()
            self.measured_fps.append(1000 / max(dt(self.t_last_fps, t0), 1))
            if len(self.measured_fps) > 30:
                self.measured_fps.pop(0)
            self.t_last_fps = t0
            self.fps = statistics.mean(self.measured_fps)
            # show table:
            if settings.show_table:
                cv2.imshow('table_sim', cv2.resize(table_image, (540, 960)))
                cv2.resizeWindow('table_sim', 540, 960)
            # show Beamer
            Beamer.show_image(beamer_image, self.beamer.rotation)
            debug(
                'display: index: {}  @{:2.1f}fps (~{:.0f}ms)   in_frames: {}  out_frames: {}  cam_q: {}   det_q: {}   bt_q: {}   disp_q: {}'.format(
                    index, self.fps, 1000 / self.fps, in_frames, out_frames, cam_q, det_q, bt_q, disp_q),
                settings.DEBUG)
            # wait 40ms max:
            wait_time = max(20 - dt(t0, now()), 1)
            self.key = cv2.waitKey(wait_time) & 0xFF
            # wait for keypressed:
            # self.key = cv2.waitKey(0) & 0xFF
            if self.key == ord('q') or self.key == 27:
                self.stopped = True
                break
            index += 1
            if index == self.queue_size:
                index = 0
        print('Stopping after {} seconds'.format(dt(t_start, now()) / 1000))
        cv2.destroyAllWindows()
        self.stopped = True
        self.detection.stop()
        self.camera.stop()
        self.bluetooth.stop()

    @staticmethod
    def get_json_from_balls(index, balls):
        json_array = {}
        ball_id = 0
        for ball in balls:
            json_array[ball_id] = {"x": int(ball.x), "y": int(ball.y), "v": ball_value(ball.color)}
            ball_id += 1
        json_string = json.dumps({"index": index, "balls": json_array})
        debug(json_string, settings.VERBOSE)
        return json_string

    def handle_dt_message(self):
        """
        Handle detection output
        """
        while True and not self.stopped:
            t0 = now()
            # process balls from detection queue
            try:
                index, balls = self.detection.output_q.get_nowait()
                debug('handle_dt: index: {} started'.format(index), settings.DEBUG)
            except queue.Empty:  # detection queue empty
                wait(20)
                continue
            json_string = self.get_json_from_balls(index, balls)
            if self.bluetooth.is_connected:
                self.bluetooth.send(json_string)
            else:
                self.bluetooth.output_q.put(json_string)
            debug('handle_dt: index: {}: {:2d}ms'.format(index, dt(t0, now())), settings.DEBUG)

    def handle_bt_message(self):
        """
        Handle bluetooth message from App
        """
        while True and not self.stopped:
            t0 = now()
            # process message from bluetooth queue
            objects = self.bluetooth.output_q.get()
            try:
                message = json.loads(objects)
            except JSONDecodeError:
                print('\n' + objects)
                print('json error.')
                traceback.print_exc()
                continue
            objects = []
            try:
                index = int(message["index"])
                if index == -1:
                    continue
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
                if self.bluetooth.is_connected:
                    self.bluetooth.send(1)
            except BaseException:
                traceback.print_exc()
                index = None
            debug('handle_bt: index: {}:  {}ms'.format(index, dt(t0, now())), settings.DEBUG)

    def display(self):
        # read a frame from cam queue and start a detection on it
        while True and not self.stopped:
            t0 = now()
            try:
                index, objects = self.display_q.get_nowait()
                debug('display_calc: index: {} started'.format(index), settings.DEBUG)
            except queue.Empty:  # display queue empty
                wait(20)
                continue
            beamer_image = Beamer.draw_objects(objects, self.beamer.outPict,
                                               self.beamer.offset_x,
                                               self.beamer.offset_y,
                                               self.beamer.ppm_x,
                                               self.beamer.ppm_y)
            cv2.putText(beamer_image, '@{:2.1f}fps'.format(self.fps),
                        (20, self.beamer.resolution_y - 20), cv2.FONT_HERSHEY_COMPLEX,
                        3, (255, 255, 255), 5)
            self.lock.acquire()
            while self.output_frames[index] is not '':
                self.lock.release()
                debug('display: output_frame[{}] is not \'\''.format(index), settings.DEBUG)
                wait(10)
                self.lock.acquire()
            if settings.show_table:
                self.output_frames[index] = [self.overlay_beamer(beamer_image,
                                                                 self.overlay_camera(self.input_frames[index],
                                                                                     self.table_src)), beamer_image]
            else:
                self.output_frames[index] = [cv2.resize(beamer_image, self.table_size), beamer_image]
            self.input_frames[index] = ""
            self.lock.release()
            debug('display_calc: index: {}:  {}ms'.format(index, dt(t0, now())), settings.DEBUG)

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
