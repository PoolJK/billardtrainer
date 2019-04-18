#!/usr/bin/python3

from threading import Thread, Lock
import os
import re
import time
import queue
from queue import Queue

import cv2
import numpy as np


class InputStream:
    def __init__(self, device, height=None, width=None, queue_size=1, debug=False):
        self.debug = debug
        self.onpi = cv2.getVersionMajor() < 4
        self.device = device
        self.stopped = True
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True
        self.last_queued = self.last_read = self.last_received = self.start = now()
        self.height = height or 1080
        self.width = width or 1920
        self.d_fps = []
        self.s_fps = []
        self.Q = Queue(queue_size)
        self.last = None
        self.stream = self.open(device)

    def open(self, device=None):
        if hasattr(self, 'stream') and self.stream.isOpened():
            pass
        else:
            if device is None:
                if self.device is None:
                    print('InputStream: open: error opening stream: no device specified')
                    return 0
                device = self.device
            self.stream = cv2.VideoCapture(device)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.width = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.last_queued = self.last_read = self.last_received = self.start = now()
        self.d_fps = []
        # V4L doesn't support fps property
        if device == 0:
            self.d_fps.append(1)
        else:
            self.d_fps.append(self.stream.get(cv2.CAP_PROP_FPS))
        self.s_fps = []
        self.s_fps.append(0.0)
        self.stopped = False
        return self.stream

    def start_capture(self):
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True
        self.t.start()
        return self

    def update(self):
        while True:
            n = now()
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # check time since last received image
            if dt(self.last_received, n) > 10000:
                if self.debug:
                    lp('InputStream.thread: input timed out after 10s, stopping')
                self.stop_capture()
                return
            # read the next frame
            try:
                grabbed, frame = self.stream.read()
            except Exception as e:
                lp('error grabbing frame: {}'.format(e))
                grabbed, frame = None, None
            if grabbed:
                t_s_last = dt(self.last_received, n)
                self.last_received = n
                if 16 < t_s_last < 2000:
                    self.s_fps.append(1000/t_s_last)
                else:
                    self.s_fps.append(0)
                # push one out if full
                if self.Q.full():
                    try:
                        self.Q.get_nowait()
                    except queue.Empty:
                        pass
                self.Q.put(frame)
                self.last_queued = n
            else:
                time.sleep(1)

    def set(self, p1, p2):
        # set flags of stream (if exists)
        if not hasattr(self, 'stream'):
            if self.debug:
                print('InputStream: set called, but stream is None')
            return 0
        ret = self.stream.set(p1, p2)
        self.height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        return ret

    def get(self, args):
        # return flags of stream
        if not hasattr(self, 'stream'):
            return 0
        return self.stream.get(args)

    def get_display_fps(self):
        if len(self.d_fps) == 10:
            self.d_fps.remove(self.d_fps[0])
        return round(np.average(self.d_fps), 1)

    def get_source_fps(self):
        if len(self.s_fps) == 10:
            self.s_fps.remove(self.s_fps[0])
        return round(np.average(self.s_fps), 1)

    def read(self):
        n = now()

        # check if still running TODO: needed?
        if self.stopped:
            if self.debug:
                lp('InputStream: failed read: source is stopped')
            return 0

        # check source is still sending frames
        if dt(self.last_received, n) > 10000:
            if self.debug:
                lp('InputStream: source timed out during read(), stopping')
            self.stop_capture()
            return 0

        # get frame from Queue, None if timeout
        try:
            frame = self.Q.get(timeout=5)
        except queue.Empty:
            frame = None
        if frame is None:
            print('InputStream: timeout in read')
            return 0

        # update fps data
        d_fps = self.get_display_fps()
        s_fps = self.get_source_fps()
        t_s_read = dt(self.last_read, n)
        if t_s_read > 50/3:
            self.d_fps.append(1000 / t_s_read)
        else:
            self.d_fps.append(0)
        self.last_read = n

        # put queue- and timestamp on it
        cv2.putText(frame, 'q:{} tsl:{: 3d}ms fps:{:02.1f}(display) {:02.1f}(source)'
                    .format(self.Q.qsize() + 1, t_s_read, d_fps, s_fps),
                    (0, frame.shape[0]), cv2.FONT_HERSHEY_COMPLEX, max(.5, frame.shape[0] / 800),
                    (255, 255, 255))
        self.last = frame
        return frame

    def stop_capture(self):
        self.stopped = True
        if self.t.is_alive():
            self.t.join()
        try:
            self.stream.release()
        except Exception as e:
            print(e)


def lp(msg):
    # lock protected print in Threads
    lock = Lock()
    lock.acquire()
    print(msg)
    lock.release()


def dt(t1, t2):
    # time difference as int in [ms]
    return int((t2-t1)*1000)


def now():
    # current time
    return time.time()


class Camera:

    height = 0
    width = 0
    fps = 0
    n_frames = 0
    capture = None
    calibration = None
    device = None
    debug = False
    mirror = False

    def __init__(self, args, sres=None, dres=None):
        if args.debug:
            self.debug = True
        # size of src to set or to use after reading from it
        if sres is not None:
            self.src_size = sres
        else:
            # hardcoded maximum source size
            self.src_size = (1920, 1080)
        # size of cv2 UI windows
        if dres is not None:
            self.win_size = dres
        else:
            self.win_size = self.src_size
        if args.mirror:
            self.mirror = True
        # if source is specified
        if args.filename:
            if args.filename == '0':
                args.filename = 0
            self.device = args.filename
        # else open device default (DSHOW on PC, 0 on Pi)
        else:
            self.device = cv2.CAP_DSHOW if args.pc_test else 0
        # camera_test flag set?
        if args.camera_test:
            self.camera_test(self.device)
        elif args.preview:
            self.show_preview(self.device)
        else:
            # run calibration
            self.calibrate_cam(args.cal_filename)

    # method to calibrate optical parameters
    def calibrate_cam(self, cal_filename=None, show_help=True, interactive=True, image_points=None):
        # save specified device to temporary variable
        old_device = self.device
        if image_points is None:
            image_points = []
        # if a separate calibration is specified and it is comma separated files
        if isinstance(cal_filename, str):
            if ',' in cal_filename:
                for f in cal_filename.split(','):
                    self.calibrate_cam(f, False, False, image_points)
                return 0
            elif '*' in cal_filename:
                # select all files with selector
                files_list = os.listdir(os.path.dirname(cal_filename))
                reg_exp = os.path.basename(cal_filename).replace('*', '[0-9]+')
                found = False
                for file in files_list:
                    if re.match(reg_exp, file):
                        found = True
                        self.calibrate_cam(os.path.dirname(cal_filename) + '/' + file, False, False, image_points)
                if not found:
                    print('No files found matching {}'.format(cal_filename))
                return 0
            if self.debug:
                print('calibration file: {}'.format(cal_filename))
            self.prepare_capture(cal_filename, quiet=True)
        # no calibration specified, use input feed
        else:
            self.prepare_capture(cal_filename)
        # help me, I don't know what to do!
        if show_help and interactive:
            print("\'c\': capture image | \'+\'/\'-\': in-/decrease balance | \'r\': remove last image"
                  "| \'q\', \'n\': next image or finish calibration | \'ESC\': exit")

        # calibration grid definition (chessboard_9x6.png)
        grid = (9, 6)

        if interactive:
            # cv2.namedWindow('bw', cv2.WINDOW_NORMAL)
            cv2.namedWindow('cal', cv2.WINDOW_NORMAL)
            cv2.namedWindow('src', cv2.WINDOW_NORMAL)

        # termination criteria for sub pixel corner detection
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # new matrix alpha
        balance = .5

        # params for bw threshold
        block_size = 133
        con = 4

        # calibration loop
        file_n = 0
        while True:
            start = now()

            # get frame
            src = self.pull_frame()
            if src is None:
                print('error in calibration: couldn\'t read src')
                return 0
            t0 = now()

            # find corners
            gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, con)
            """
            # search in src first, if not finding any, search the processed frames
            for tmp in [src, gray, bw]:
                ret, corners = cv2.findChessboardCorners(tmp, (grid[0], grid[1]), None, flags=cv2.CALIB_CB_FAST_CHECK)
                if ret:
                    break
            """
            ret, corners = cv2.findChessboardCorners(bw, grid, None, flags=cv2.CALIB_CB_FAST_CHECK)
            t1 = now()

            # if corners have been found
            if ret:
                # sub pixel refine corners
                corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                src = cv2.drawChessboardCorners(src, grid, corners, ret)
            t2 = now()

            # display everything if interactive
            # if a calibration is available, output the calibrated frame as well
            if interactive and self.calibration is not None:
                cal = self.calibrate_image(src)
                cv2.imshow('cal', cv2.resize(cal, self.win_size))
                cv2.resizeWindow('cal', self.win_size[0], self.win_size[1])
            if interactive:
                # cv2.imshow('bw', cv2.resize(bw, self.win_size))
                # cv2.resizeWindow('bw', self.win_size[0], self.win_size[1])
                # marker if corners are found or not
                cv2.circle(src, (30, 30), 20, (0, 0, 255) if corners is None else (0, 255, 0), -1)
                cv2.imshow("src", cv2.resize(src, self.win_size))
                cv2.resizeWindow('src', self.win_size[0], self.win_size[1])
            t3 = now()

            # ganz hässlicher hack fürs automatische laden:
            if not interactive:
                key = ord('c')
            else:
                if self.debug:
                    print('\rloop={: 4d}ms - t0={: 4d}ms t1={: 4d}ms t2={: 4d}ms t3={: 4d}ms'
                          .format(dt(start, now()), dt(start, t0), dt(t0, t1), dt(t1, t2), dt(t2, t3)), end='')
                if self.n_frames == 1:
                    # only one frame, show until keypress
                    key = cv2.waitKey() & 0xFF
                else:
                    # more than one or no frame, don't wait until showing next
                    key = cv2.waitKey(1) & 0xFF

            # process key inputs
            if key == ord('c'):
                # add current image to calibration
                if corners is None:
                    print('\nno corners detected, can\'t calibrate')
                else:
                    image_points.append(corners)
                    # calibrate camera (add new image points to existing calibration
                    self.perform_calibration(gray, image_points, grid, balance)
                    # save to file
                    if interactive:
                        path = 'resources/experimental/'
                        if not os.path.isdir(path):
                            os.makedirs(path)
                        while os.path.isfile(path+'cal{:02d}.jpg'.format(file_n)):
                            file_n += 1
                        cv2.imwrite('resources/experimental/cal{:02d}.jpg'.format(file_n), gray)
                    # if not a stream go to next
                    if self.n_frames > 0:
                        break
            elif key in (ord('q'), ord('n')):
                # next image or finish
                if self.debug and interactive:
                    print('')
                break
            elif key == ord('+'):
                block_size += 2
                balance = balance + 0.1 if balance < 0.9 else 1
                print("\nbalance = {}".format(balance))
                self.perform_calibration(gray, image_points, grid, balance)
            elif key == ord('-'):
                block_size = block_size - 2 if block_size > 3 else 1
                balance = balance - 0.1 if balance > 0.1 else 0
                print("\nbalance = {}".format(balance))
                self.perform_calibration(gray, image_points, grid, balance)
            elif key == ord('ü'):
                con += 1
                print("\ncon = {}".format(con))
            elif key == ord('.'):
                print("\ncon = {}".format(con))
                con -= 1
            elif key == ord('r'):
                print("\nremoving last image")
                image_points.pop()
                os.remove('resources/experimental/cal{:02d}.jpg'.format(file_n))
                file_n -= 1
                self.perform_calibration(gray, image_points, grid, balance)
            elif key == 27:
                # exit
                self.stop_capture()
                cv2.destroyAllWindows()
                exit(0)
        self.stop_capture()
        self.device = old_device
        cv2.destroyAllWindows()

    def perform_calibration(self, gray_image, image_points, grid, balance):
        # scale = distance between chessboard corners in mm ?
        scale = 1
        calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_FIX_SKEW
        k = np.zeros((3, 3))
        d = np.zeros((4, 1))
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(grid[0],grid[1],0)
        object_points_grid = np.zeros((1, grid[0] * grid[1], 3), np.float32)
        object_points_grid[0, :, :2] = np.mgrid[0:scale * grid[0]:scale, 0:scale * grid[1]:scale].T.reshape(-1, 2)

        # fill object_points array
        object_points = [object_points_grid] * len(image_points)

        # calibrate according to various tutorial sources...
        rms, k, d, rvecs, tvecs = cv2.fisheye.calibrate(object_points, image_points, gray_image.shape[::-1], k, d,
                                                        flags=calibration_flags, criteria=(cv2.TERM_CRITERIA_EPS +
                                                                                           cv2.TERM_CRITERIA_MAX_ITER,
                                                                                           30, 1e-6))
        new_k = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(k, d, gray_image.shape[::-1], np.eye(3),
                                                                       balance=balance)
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(k, d, np.eye(3), new_k, gray_image.shape[::-1], cv2.CV_16SC2)
        self.calibration = {'k': k, 'd': d, 'map1': map1, 'map2': map2}

    def calibrate_image(self, src):
        # TODO: cropping ?
        out = cv2.remap(src, self.calibration['map1'], self.calibration['map2'],
                        interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        return out

    # method to return calibrated frame
    def pull_cal_frame(self, src=None):
        # get frame from input
        src = self.pull_frame(src)
        # if no calibration available, return frame
        if not self.calibration or src is 0:
            return src, src
        return src, self.calibrate_image(src)

    # method to return a frame
    def pull_frame(self, src=None):
        if src is None:
            if self.capture is None or self.capture.stopped:
                self.prepare_capture(quiet=True)
            src = self.capture.read()
        if src is 0 or src is None:
            return None
        # if single frame is source: TODO: handle better
        if 0 < self.n_frames <= self.capture.get(cv2.CAP_PROP_POS_FRAMES):
            # reopen capture
            self.stop_capture()
            self.prepare_capture(quiet=True)
        if self.mirror:
            src = cv2.flip(src, 1)
        # standard image size during testing
        if self.debug and self.src_size is not None:
            return cv2.resize(src, self.src_size, cv2.INTER_CUBIC)
        else:
            return src

    # method to prepare capture
    def prepare_capture(self, device=None, quiet=False):
        # capture already set?
        if self.capture:
            # capture open?
            if not self.capture.stopped:
                return
            # print('capture set but not open, trying to reopen')
            self.capture.open()
        # capture not yet set:
        else:
            # device specified? else use default
            if device is None:
                device = self.device
            else:
                # if filename, try to accept ommitting resources/experimental:
                if os.path.isfile('resources/experimental/{0}'.format(device)):
                    device = 'resources/experimental/{0}'.format(device)
                elif os.path.isfile('resources/{0}'.format(device)):
                    device = 'resources/{0}'.format(device)
                self.device = device
            # open capture queue
            self.capture = InputStream(device, self.src_size[1], self.src_size[0], debug=self.debug)
        # capture queue is definitely open at this point
        # replace with better structure if you can
        self.capture.start_capture()
        # TODO: move first read to open function
        # wait for first read (blocking call for 5s, None if timed out)
        if self.capture.read() is None:
            print('camera: error, couldn\'t start capture')
            return 0
        # get input data
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if self.win_size is None:
            self.win_size = (self.width, self.height)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        if self.fps == 0:
            self.fps = 25
        # workaround V4L doesn't support frame_count, stream return some weird negative number:
        if device is not None and device is not 0:
            self.n_frames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        else:
            self.n_frames = -1
        if self.n_frames < 0:
            self.n_frames = -1
        if self.debug and not quiet:
            print('prepare_capture: captured src {}x{}@{}fps n_frames={}'.format(self.width, self.height, self.fps, self.n_frames))

    # method to end capture
    def stop_capture(self):
        self.capture.stop_capture()

    # method to display all available resolutions from input
    def camera_test(self, device):
        """ test 1: get available resolutions """
        # better idea: use 'v4l2-ctl --list-formats-ext' (sudo apt-get install v4l-utils" if not installed)
        # clean up device name for saving:
        import string
        valid_chars = "-_() %s%s" % (string.ascii_letters, string.digits)
        replace_chars = ".:/"
        s = str(device)
        for c in replace_chars:
            s = s.replace(c, '_')
        s = ''.join(c for c in s if c in valid_chars)
        cap = cv2.VideoCapture(device)
        path = 'resources/experimental/camera_test/'
        if not os.path.isdir(path):
            os.makedirs(path)

        # start low
        frame_width = 16
        # loop high
        while frame_width < 4000:
            # advance resolution
            frame_width += 16
            # test 16:9, 16:10, 4:3
            for frame_height in np.arange(int(frame_width / 16 * 9) - int(frame_width / 16 * 9) % 4, frame_width, 4):
                # have to set width first, else height might not be set
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
                # calculate aspect string
                aspect = int(frame_height / frame_width * 16)
                if aspect == 12:
                    aspect = '4:3'
                else:
                    aspect = '16:{}'.format(aspect)
                # measure actual dims in source
                measured_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                measured_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                print('\rset: {: 4d}x{: 4d} measured: {: 4d}x{: 4d}'.format(frame_width, frame_height, measured_width,
                                                                            measured_height), end='')
                # if measure equals set, save and display result
                if measured_height == frame_height and measured_width == frame_width:
                    r, img = cap.read()
                    cv2.imwrite('{}/{}x{}_dev={}.jpg'.format(path, frame_width, frame_height, s), img)
                    # log
                    print('\nfound: {}x{} ({})'.format(frame_width, frame_height, aspect))
        cap.release()
        """ test 2: try out modes
        self.prepare_capture(device, quiet=True)
        mode = 0
        cv2.namedWindow('preview', cv2.WINDOW_NORMAL)
        cv2.imshow('preview', self.pull_frame())
        cv2.resizeWindow('preview', self.win_size[0], self.win_size[1])
        while True:
            print('\rmode={}, trying mode={}: '.format(self.capture.get(cv2.CAP_PROP_MODE), mode), end='')
            self.capture.set(cv2.CAP_PROP_MODE, mode)
            cv2.imshow('preview', self.pull_frame())
            mode += 1
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        self.stop_capture() 
        """

    def show_preview(self, device):
        self.prepare_capture(device)
        while True:
            cv2.imshow('preview', self.pull_frame())
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        self.stop_capture()
