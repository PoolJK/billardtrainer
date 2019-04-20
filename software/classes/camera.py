#!/usr/bin/python3

import os
import re
from classes.utils import *
from classes.input_stream import InputStream


class Camera:

    fps = 0
    n_frames = 0
    capture = None
    calibration = None
    is_calibrated = False
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
        if not args.calibrate:
            self.load_calibration()
        # camera_test flag set?
        if args.camera_test:
            self.camera_test(self.device)
        elif args.preview:
            self.show_preview(self.device)

    def load_calibration(self):
        dirname = self.device
        replace = ':./'
        for r in replace:
            dirname = dirname.replace(r, '_')
        path = 'resources/calibration/' + dirname
        if not os.path.isdir(path):
            return 0
        self.calibration = {}
        try:
            cal = np.load(path + '/cal.npz')
            for key in cal:
                self.calibration[key] = cal[key]
        except Exception as e:
            print('camera: error reading calibration file', e)
            self.calibration = None
            return 0
        if len(self.calibration) >= 3:
            self.is_calibrated = True
        else:
            self.calibration = None
        return self.is_calibrated

    def save_calibration(self):
        if self.calibration is None:
            return 0
        dirname = self.device
        replace = ':./'
        for r in replace:
            dirname = dirname.replace(r, '_')
        path = 'resources/calibration/' + dirname + '/'
        if not os.path.isdir(path):
            os.makedirs(path)
        np.savez(path + 'cal', **self.calibration)

    def auto_calibrate(self, beamer, device=None):
        if device is None:
            device = self.device
        old_device = self.device
        self.prepare_capture(device)
        # calibration grid definition (chessboard_9x6.png)
        grid = (9, 6)
        # load pattern file to display
        pattern = cv2.imread('resources/chessboard_9x6.png')
        # scale pattern
        # pattern width in pixels
        pattern_size = (int(beamer.width / 2), int(beamer.width / 2 * pattern.shape[0] / pattern.shape[1]))
        pattern = cv2.resize(pattern, pattern_size)

        cv2.namedWindow('bw', cv2.WINDOW_NORMAL)
        cv2.namedWindow('cal', cv2.WINDOW_NORMAL)
        cv2.namedWindow('src', cv2.WINDOW_NORMAL)

        # termination criteria for sub pixel corner detection
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # new matrix alpha
        balance = 0.1

        # params for bw threshold
        block_size = 55
        constant = 4

        # calibration loop
        # pattern positions:
        p_positions = [
            (int((beamer.width - pattern_size[0])/2), int((beamer.height - pattern_size[1])/2), 0, 1),
            # center
            (0, (beamer.height - pattern_size[1]) / 2, 0, 1),  # left
            (beamer.width - pattern_size[0], (beamer.height - pattern_size[1]) / 2, 0, 1),  # right
            # (int((beamer.width - pattern_size[0]) / 2), 0, 0, 1),  # top
            #  (int((beamer.width - pattern_size[0]) / 2), beamer.height - pattern_size[1], 0, 1),  # bottom
            (beamer.width - pattern_size[0], beamer.height - pattern_size[1] - 80, -10, 1),
            # right lower corner
            (0, beamer.height - pattern_size[1] - 80, 15, 1),  # left lower corner
            (beamer.width - pattern_size[0], -40, -5, 1),  # right upper corner
            (0, -40, 0, 1),  # left upper corner
            # (0, 0, 0, 0),  # fullscreen
            # (0, 40, -20, 1),
            # (beamer.width - pattern_size[0], 70, 20, 1),
            # (beamer.width - pattern_size[0], beamer.height - pattern_size[1] - 100, 170, 1),
            # (-40, beamer.height - pattern_size[1] - 60, -170, 1),
            # (0, int((beamer.height - pattern_size[1]) / 2), -45, 1)]
        ]
        # try twice:
        # p_positions.extend(p_positions)
        beamer.window('pattern', cv2.WINDOW_NORMAL)
        image_points = []
        for position in p_positions:
            # print('\nposition={}'.format(position))
            # rotate the image and recalculate position
            _s = pattern.shape[:2]
            pat = rotate_bound(pattern, position[2])
            if pat.shape[1] > _s[1]:
                p0 = int(position[0] - (pat.shape[1] - _s[1]) / 2)
            else:
                p0 = int(position[0] + (pat.shape[1] - _s[1]) / 2)
            if pat.shape[0] > _s[0]:
                p1 = int(position[1] - (pat.shape[0] - _s[0]) / 2)
            else:
                p1 = int(position[1] + (pat.shape[0] - _s[0]) / 2)
            position = (p0, p1, position[2], position[3])
            beamer.show('pattern', pat, position)

            # count n of rejected position takes
            rejected = 0
            while True:
                if rejected >= 10:
                    print('\nposition rejected')
                    break
                start = now()

                # get frame
                src = self.pull_frame()
                if src is None:
                    print('error in calibration: couldn\'t read src')
                    return 0
                t0 = now()

                # find corners
                gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
                bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, block_size, constant)
                # search in src first, if not finding any, search the processed frames
                for tmp in [src, gray, bw]:
                    ret, corners = cv2.findChessboardCorners(tmp, (grid[0], grid[1]), None,
                                                             flags=cv2.CALIB_CB_FAST_CHECK)
                    if ret:
                        break
                # ret, corners = cv2.findChessboardCorners(bw, grid, None, flags=cv2.CALIB_CB_FAST_CHECK)
                t1 = now()

                # if corners have been found
                if ret:
                    # sub pixel refine corners
                    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    src = cv2.drawChessboardCorners(src, grid, corners, ret)
                t2 = now()

                # display everything
                # if a calibration is available, output the calibrated frame as well
                if self.calibration is not None:
                    cal = self.undistort_image(src)
                    cv2.imshow('cal', cv2.resize(cal, self.win_size))
                cv2.imshow('bw', cv2.resize(bw, self.win_size))
                # marker if corners are found or not
                cv2.circle(src, (30, 30), 20, (0, 0, 255) if corners is None else (0, 255, 0), -1)
                cv2.imshow("src", cv2.resize(src, self.win_size))
                cv2.resizeWindow('src', self.win_size[0], self.win_size[1])
                t3 = now()

                if self.debug:
                    print('\rloop={: 4d}ms - t0={: 4d}ms t1={: 4d}ms t2={: 4d}ms t3={: 4d}ms'
                          .format(dt(start, now()), dt(start, t0), dt(t0, t1), dt(t1, t2), dt(t2, t3)), end='')
                if self.n_frames == 1:
                    # only one frame, show until keypress
                    key = cv2.waitKey() & 0xFF
                else:
                    # more than one or no frame, don't wait until showing next
                    key = cv2.waitKey(1) & 0xFF

                # this has to be after waitKey
                if corners is not None:
                    # show white image so position won't be falsely read twice
                    white = np.ones(pat.shape, np.uint8) * 255
                    beamer.show('pattern', white, position)
                    cv2.waitKey(1)
                    image_points.append(corners)
                    # calibrate camera (add new image points to existing calibration
                    if self.perform_calibration(gray, image_points, grid, balance):
                        # cv2.waitKey()
                        # stream delay
                        wait(800)
                        break
                    else:
                        # error or image rejected
                        beamer.show('pattern', pat, position)
                        image_points.pop()
                        rejected += 1
                        continue
                # process key inputs
                if key == 27 or key == ord('q'):
                    print('\nbye')
                    cv2.destroyAllWindows()
                    self.stop_capture()
                    exit(0)
        self.save_calibration()
        self.stop_capture()
        self.device = old_device
        cv2.destroyAllWindows()
        self.is_calibrated = True

    # method to calibrate optical parameters
    def manual_calibrate(self, beamer, cal_filename=None, show_help=True, interactive=True, image_points=None):
        # save specified device to temporary variable
        old_device = self.device
        if image_points is None:
            image_points = []
        # if a separate calibration is specified and it is comma separated files
        if isinstance(cal_filename, str):
            if ',' in cal_filename:
                for f in cal_filename.split(','):
                    self.manual_calibrate(beamer, f, False, False, image_points)
                return 0
            elif '*' in cal_filename:
                # select all files with selector
                files_list = os.listdir(os.path.dirname(cal_filename))
                reg_exp = os.path.basename(cal_filename).replace('*', '[0-9]+')
                found = False
                for file in files_list:
                    if re.match(reg_exp, file):
                        found = True
                        self.manual_calibrate(beamer,
                                              os.path.dirname(cal_filename) + '/' + file,
                                              False, False, image_points)
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
            beamer.window('cal', cv2.WINDOW_NORMAL)
            beamer.window('src', cv2.WINDOW_NORMAL)

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
                cal = self.undistort_image(src)
                beamer.show('cal', cv2.resize(cal, self.win_size))
            if interactive:
                # cv2.imshow('bw', cv2.resize(bw, self.win_size))
                # cv2.resizeWindow('bw', self.win_size[0], self.win_size[1])
                # marker if corners are found or not
                cv2.circle(src, (30, 30), 20, (0, 0, 255) if corners is None else (0, 255, 0), -1)
                beamer.show("src", cv2.resize(src, self.win_size))
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
        calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC  + cv2.fisheye.CALIB_FIX_SKEW
        k = np.zeros((3, 3))
        d = np.zeros((4, 1))

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(grid[0],grid[1],0)
        object_points_grid = np.zeros((1, grid[0] * grid[1], 3), np.float32)
        object_points_grid[0, :, :2] = np.mgrid[0:scale * grid[0]:scale, 0:scale * grid[1]:scale].T.reshape(-1, 2)

        # fill object_points array
        object_points = [object_points_grid] * len(image_points)

        """ method 1: fisheye """
        # calibrate according to various tutorial sources...
        try:
            rms, k, d, rvecs, tvecs = cv2.fisheye\
                .calibrate(object_points, image_points, gray_image.shape[::-1], k, d,
                           flags=calibration_flags, criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                                                              50, 0.5))
        except cv2.error as e:
            print('\nerror in calibration function:', e)
            return 0
        print('\nrms={}'.format(rms))
        # if rms too high, reject
        if rms > 20 or (self.calibration is not None and rms > self.calibration['rms']):
            print('\nrms too high: {}'.format(rms))
            return 0
        new_k = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(k, d, gray_image.shape[::-1], np.eye(3),
                                                                       balance=balance)
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(k, d, np.eye(3), new_k, gray_image.shape[::-1], cv2.CV_16SC2)
        """ method 2: normal """
        r, mtx, dist, rv, tv = cv2.calibrateCamera(object_points, image_points,
                                                   gray_image.shape[::-1], None, None)
        self.calibration = {'size': gray_image.shape[::-1],
                            'map1': map1, 'map2': map2, 'rms': rms,
                            'mtx': mtx, 'dist': dist}
        return 1

    def undistort_image(self, src):
        # TODO: cropping ?
        # also TODO: scaling
        src = cv2.resize(src, tuple(self.calibration['size']))
        if self.calibration['rms'] < 2:  # fisheye error low
            """ method 1: fisheye """
            out = cv2.remap(src, self.calibration['map1'], self.calibration['map2'],
                            interpolation=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
        else:  # normal camera better
            """ method 2: normal """
            new_mtx, roi = cv2.getOptimalNewCameraMatrix(self.calibration['mtx'], self.calibration['dist'],
                                                         self.calibration['map1'].shape[:2], 1, src.shape[:2])
            out = cv2.undistort(src, self.calibration['mtx'], self.calibration['dist'], None, new_mtx)
            y, x, h, w = roi
            if w > 0 and h > 0:
                cropped = out[y:y+h, x:x+w]
                cv2.imshow('cropped', cropped)
        return out

    # method to return calibrated frame
    def pull_cal_frame(self, src=None):
        # get frame from input
        src = self.pull_frame(src)
        # if no calibration available, return frame
        if not self.is_calibrated or src is 0:
            return src, src
        return src, self.undistort_image(src)

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
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        if self.mirror:
            src = cv2.flip(src, 1)
        # standard image size during testing
        if self.debug and self.src_size is not None:
            return cv2.resize(src, self.src_size, cv2.INTER_CUBIC)
        else:
            return src

    # method to prepare capture
    def prepare_capture(self, device=None, quiet=False):
        # device specified? else use default
        if device is None:
            device = self.device
        else:
            # if filename, try to accept ommitting resources/experimental:
            if os.path.isfile('resources/experimental/{0}'.format(device)):
                device = 'resources/experimental/{0}'.format(device)
            elif os.path.isfile('resources/{0}'.format(device)):
                device = 'resources/{0}'.format(device)
            # device specified, save to default
            self.device = device
        # capture already set?
        if self.capture:
            # capture open?
            if not self.capture.stopped:
                return
            # capture set but not open, try to reopen if same device
            if self.capture.device == device:
                self.capture.open()
            else:
                # create new
                self.capture.stop_capture()
                self.capture = InputStream(device, self.src_size[1], self.src_size[0], debug=self.debug)
        # capture not yet set:
        else:
            # open capture queue
            self.capture = InputStream(device, self.src_size[1], self.src_size[0], debug=self.debug)
        self.capture.start_capture()
        # TODO: move first read to open function ?
        # wait for first read (blocking call for 5s, None if timed out)
        f = self.capture.read()
        # cv2.imshow('f', cv2.resize(f, self.win_size))
        if f is None:
            print('camera: error, couldn\'t start capture')
            return
        # get input data
        self.src_size = (int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                         int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        if self.win_size is None:
            self.win_size = self.src_size
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
            print('prepare_capture: captured src {}x{}@{}fps n_frames={}'
                  .format(self.src_size[0], self.src_size[1], self.fps, self.n_frames))

    # method to end capture
    def stop_capture(self):
        self.capture.stop_capture()

    # method to display all available resolutions from input
    @staticmethod
    def camera_test(device):
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
            src, cal = self.pull_cal_frame()
            cv2.imshow('src', src)
            if cal is not None:
                cv2.imshow('cal', cal)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        self.stop_capture()
