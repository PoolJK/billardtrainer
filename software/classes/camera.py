# the camera wants a class too :'-/

import cv2
import time
import numpy as np


class Camera:

    height = 0
    width = 0
    fps = 0
    n_frames = 0
    capture = None
    calibration = None
    device = None
    win_size = None
    standard_size = None
    debug = False

    def __init__(self, args, win_size=None):
        if args.debug:
            self.debug = True
            self.standard_size = (1280, 720)
            print('set standard_size = {}'.format(self.standard_size))
        # size of cv2 windows
        if win_size:
            self.win_size = win_size
        # if source is specified
        if args.filename:
            self.device = args.filename
        # else open device default (DSHOW on PC, 0 on Pi)
        else:
            self.device = cv2.CAP_DSHOW if args.pc_test else 0
        # run calibration
        self.calibrate_cam(args.cal_filename)

    # method to calibrate optical parameters
    def calibrate_cam(self, filename=None, show_help=True):
        start = time.time()
        # save specified device to temporary variable
        old_device = self.device
        # if a separate calibration is specified and it is comma separated files
        if isinstance(filename, str) and ',' in filename:
            for f in filename.split(','):
                self.calibrate_cam(f, False)
            return 0
        # no calibration specified, use input feed
        else:
            self.prepare_capture(filename)
        # help me, I don't know what to do!
        if show_help:
            print("\'c\': capture image | \'+\'/\'-\': in-/decrease alpha | \'r\': reset calibration"
                  "| \'q\': next image or finish calibration | \'ESC\': exit")

        # calibration grid definition (chessboard_9x6.png)
        grid = [9, 6]
        scale = 10  # mm between corners

        cv2.namedWindow('src', cv2.WINDOW_NORMAL)
        cv2.namedWindow('bw', cv2.WINDOW_NORMAL)
        cv2.namedWindow('cal', cv2.WINDOW_NORMAL)

        # termination criteria for sub pixel corner detection
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(grid[0],grid[1],0)
        object_points_grid = np.zeros((grid[1] * grid[0], 3), np.float32)
        object_points_grid[:, :2] = np.mgrid[0:scale * grid[0]:scale, 0:scale * grid[1]:scale].T.reshape(-1, 2)
        # print(object_points_grid)
        # prepare empty arrays for found corner points
        object_points = []
        image_points = []

        # new matrix alpha
        alpha = 1

        # params for bw threshold
        block_size = 133
        con = 4

        # screen text params
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        line_scale = 20
        font_color = (255, 255, 255)
        line_type = 1

        if self.debug:
            print('setup time: {}ms'.format(int((time.time()-start)*1000)))
        # calibration loop
        while True:
            start = time.time()
            # new frame, reinit text position
            pos = (10, 70)

            # get frame
            src = self.pull_frame()
            src_time = int((time.time()-start)*1000)
            if src is None:
                print('error in calibration: couldn\'t read src')
                return 0
            gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, con)

            # find corners
            # search in src first, if not finding any, search the processed frames
            for tmp in [src, gray, bw]:
                ret, corners = cv2.findChessboardCorners(tmp, (grid[0], grid[1]), None, flags=cv2.CALIB_CB_FAST_CHECK)
                if ret:
                    break
            if ret:
                # if corners have been found
                # sub pixel refine corners
                corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                src = cv2.drawChessboardCorners(src, (grid[0], grid[1]), corners, ret)
            # display everything
            detect_time = int((time.time()-start)*1000) - src_time
            # if a calibration is available, output the calibrated frame as well
            cal_time = 0
            if self.calibration is not None:
                cal = self.pull_cal_frame(src)
                cv2.imshow('cal', cv2.resize(cal, self.win_size))
                cv2.resizeWindow('cal', self.win_size[0], self.win_size[1])
                # use region of interest for cropping
                # the roi vector is weird. I think, cv itself doesn't know what it's doing here.
                x, y, w, h = self.calibration['roi']
                roi = cal[y:y+h, x:x+w]
                try:
                    cv2.imshow('cal+roi', cv2.resize(roi, self.win_size))
                    cv2.resizeWindow('cal+roi', self.win_size[0], self.win_size[1])
                except cv2.error:
                    print('cv2.error occurred in camera->calibration')
                # TODO: why does this crash the script on Pi?
                """# write some details into the image
                with np.printoptions(precision=3, suppress=True):
                    cv2.putText(src, "mtx:", pos, font, font_scale, font_color, line_type)
                    pos = (pos[0], pos[1] + line_scale)
                    for y in self.calibration['mtx']:
                        cv2.putText(src, str(y), pos, font, font_scale, font_color, line_type)
                        pos = (pos[0], pos[1] + line_scale)
                    cv2.putText(src, "dist:", pos, font, font_scale, font_color, line_type)
                    pos = (pos[0], pos[1] + line_scale)
                    for y in self.calibration['dist']:
                        cv2.putText(src, str(y), pos, font, font_scale, font_color, line_type)
                        pos = (pos[0], pos[1] + line_scale)
                    cv2.putText(src, "roi: " + str(self.calibration['roi']), pos, font, font_scale, font_color,
                                line_type)
                """
                cal_time = int((time.time() - start)*1000) - detect_time
            cv2.imshow('bw', cv2.resize(bw, self.win_size))
            cv2.resizeWindow('bw', self.win_size[0], self.win_size[1])
            # marker if corners are found or not
            cv2.circle(src, (30, 30), 20, (0, 0, 255) if corners is None else (0, 255, 0), -1)
            cv2.imshow("src", cv2.resize(src, self.win_size))
            cv2.resizeWindow('src', self.win_size[0], self.win_size[1])
            if self.debug:
                print('\rmain loop time: {}ms, cal: {}ms, detect: {}ms, src: {}ms'
                      .format(int((time.time()-start)*1000), cal_time, detect_time, src_time), end='')
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
                    print('no corners detected, can\'t calibrate')
                else:
                    object_points.append(object_points_grid)
                    image_points.append(corners)
                    # calibrate camera (add new image points to existing calibration
                    # print(gray.shape[::1])
                    if self.debug:
                        print('\ncurrent calibration = {}'.format(self.get_calibration()))
                    mtx, dist, rvecs, tvecs, new_mtx, roi = self.get_calibration()
                    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(object_points, image_points, gray.shape[::-1],
                                                                       mtx, dist, rvecs, tvecs)
                    new_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (src.shape[1], src.shape[0]), alpha)
                    # save calibration
                    self.set_calibration(mtx, dist, rvecs, tvecs, new_mtx, roi)
                    print('calibration updated')
            elif key in (ord('q'), ord('n')):
                # next image or finish
                if self.debug:
                    print('')
                break
            elif key == ord('+'):
                alpha = alpha + 0.1 if alpha < 0.9 else 1
                print("alpha = {}".format(alpha))
            elif key == ord('-'):
                alpha = alpha - 0.1 if alpha > 0.1 else 0
                print("alpha = {}".format(alpha))
            elif key == ord('ü'):
                con += 1
                print("con = {}".format(con))
            elif key == ord('.'):
                print("con = {}".format(con))
                con -= 1
            elif key == ord('r'):
                print("calibration reset")
                object_points = []
                image_points = []
                self.calibration = None
            elif key == 27:
                # exit
                self.stop_capture()
                cv2.destroyAllWindows()
                exit(0)
        self.stop_capture()
        self.device = old_device
        cv2.destroyAllWindows()

    def set_calibration(self, mtx, dist, rvecs, tvecs, new_mtx, roi):
        self.calibration = {'mtx': mtx, 'dist': dist, 'rvecs': rvecs, 'tvecs': tvecs, 'new_mtx': new_mtx, 'roi': roi}

    def get_calibration(self):
        if self.calibration is not None:
            return self.calibration['mtx'], self.calibration['dist'], self.calibration['rvecs'], \
                   self.calibration['tvecs'], self.calibration['new_mtx'], self.calibration['roi']
        else:
            return None, None, None, None, None, None

    # method to return calibrated frame
    def pull_cal_frame(self, src=None):
        # get frame from input
        src = self.pull_frame(src)
        # if no calibration available, return frame
        if not self.calibration or src is None:
            return src
        # use calibration parameters to generate calibrated image
        # alternative: use warpPerspective (https://www.programcreek.com/python/example/84096/cv2.undistort)
        # or remap
        # (https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html)
        out = cv2.undistort(src, self.calibration['mtx'], self.calibration['dist'])
        # use region of interest for cropping (roi don't make much sense currently)
        # x, y, w, h = self.calibration['roi']
        # src = src[y:y+h, x:x+w]
        return out

    # method to return a frame
    def pull_frame(self, src=None):
        if src is None:
            if self.capture is None:
                self.prepare_capture()
            has_frame, src = self.capture.read()
            if not has_frame:
                print("error reading frame from specified source: {}".format(self.device))
                return None
        if 0 < self.n_frames <= self.capture.get(cv2.CAP_PROP_POS_FRAMES):
            # reopen capture
            self.stop_capture()
            self.prepare_capture()
        # standard image size during testing
        if self.debug:
            return cv2.resize(src, self.standard_size, cv2.INTER_CUBIC)
        else:
            return src

    # method to prepare capture
    def prepare_capture(self, device=None):
        # capture already set?
        if self.capture:
            # capture open?
            if self.capture.isOpened():
                print("capture already open")
                return 0
            self.capture = None
        # device specified? else use default
        if device is None:
            device = self.device
        else:
            # argparser produces string(0), need int(0)
            if device == '0':
                device = 0
            self.device = device
        # open capture
        self.capture = cv2.VideoCapture(device)
        if not self.capture.isOpened:
            print("Error opening capture! device={}".format(device))
            return 0
        # get input data
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        if self.win_size is None:
            self.win_size = (self.width, self.height)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        if self.fps == 0:
            self.fps = 25
        self.n_frames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)

    # method to end capture
    def stop_capture(self):
        self.capture.release()
        self.capture = None
