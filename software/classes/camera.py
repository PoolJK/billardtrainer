# the camera wants a class too :'-/

import cv2
import numpy as np


class Camera:

    capture = None
    calibration = None
    device = None

    def __init__(self, device):
        self.device = device
        self.prepare_capture()

    # method to calibrate optical parameters
    # opens a video capture
    # takes single images on keypress if corners are found, then adds them to the calibration calculation
    # shows source, calibrated source, processed black and white, and the detection data in live feed
    def calibrate_cam(self):
        self.prepare_capture()
        # help me, I don't know what to do!
        print("c: capture image | +/-: in-/decrease blocksize | ü/.: in-/decrease constant | r: reset calibration"
              "| ESC: exit")

        # calibration grid definition
        grid = [9, 6]
        scale = 10  # mm between corners

        # set (max) fps for scale capture
        fps = 30
        sw = 1920
        sh = 1080
        cv2.namedWindow("src")
        cv2.namedWindow("bw")
        cv2.namedWindow("cal")

        # termination criteria for sub pixel corner detection
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        object_points_grid = np.zeros((grid[1] * grid[0], 3), np.float32)
        object_points_grid[:, :2] = np.mgrid[0:scale * grid[0]:scale, 0:scale * grid[1]:scale].T.reshape(-1, 2)

        # prepare empty arrays for found corner points
        object_points = []
        image_points = []

        # params for bw threshold
        block_size = 133
        con = 4

        # screen text params
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        line_scale = 20
        font_color = (255, 255, 255)
        line_type = 1

        # capture loop
        while True:
            # new frame, reinit text position
            pos = (10, 70)

            # get frame
            src = self.pull_frame()
            gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, con)

            # find corners
            # search in src first, if not finding any, search the processed frames
            for tmp in [src, gray, bw]:
                ret, corners = cv2.findChessboardCorners(tmp, (grid[0], grid[1]), None,
                                                         flags=cv2.CALIB_CB_FAST_CHECK)
                if ret:
                    break
            if ret:
                # if corners have been found
                # sub pixel refine corners
                corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                src = cv2.drawChessboardCorners(src, (grid[0], grid[1]), corners, ret)
            """
            ret, corners = cv2.findChessboardCorners(bw, (grid[0], grid[1]), None,
                                                     flags=cv2.CALIB_CB_FAST_CHECK)
            if ret:
                corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                src = cv2.drawChessboardCorners(src, (grid[0], grid[1]), corners, ret)
            """
            # display everything
            cv2.imshow("bw", bw)
            if self.calibration is not None:
                cal = self.pull_cal_frame(src)
                cv2.imshow("cal", cal)
                # use region of interest for cropping
                # the roi vector is weird. I think, cv itself doesn't know what it's doing here.
                x, y, w, h = self.calibration['roi']
                roi = cal[y:y+h, x:x+w]
                try:
                    cv2.imshow("cal+roi", roi)
                except cv2.error:
                    pass
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
            cv2.circle(src, (30, 30), 20, (0, 0, 255) if corners is None else (0, 255, 0), -1)
            cv2.imshow("src", src)
            cv2.moveWindow("bw", -sw, int(sh / 2))
            cv2.resizeWindow("bw", int(sw/2), int(sh/2))
            cv2.moveWindow("cal", -int(sw / 2), 0)
            cv2.resizeWindow("cal", int(sw/2), int(sh/2))
            cv2.moveWindow("src", -sw, 0)
            cv2.resizeWindow("src", int(sw/2), int(sh/2))
            key = cv2.waitKey(int(1000 / fps)) & 0xFF
            # process key inputs
            if key == ord('c') and corners is not None:
                object_points.append(object_points_grid)
                image_points.append(corners)
                # calibrate camera (add new image points to existing calibration
                ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(object_points, image_points, gray.shape[::-1], None,
                                                                   None)
                new_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, src.shape[:2], 1)
                # save calibration
                self.calibration = {'mtx': mtx, 'dist': dist, 'new_mtx': new_mtx, 'roi': roi}
            elif key == ord('q'):
                break
            elif key == ord('+'):
                block_size += 2
                print("block_size = {}".format(block_size))
            elif key == ord('-'):
                block_size -= 2 if block_size > 1 else 0
                print("block_size = {}".format(block_size))
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
                self.stop_capture()
                cv2.destroyAllWindows()
                exit(0)
        self.stop_capture()
        cv2.destroyAllWindows()
        return self.calibration

    # method to prepare capture
    def prepare_capture(self, device=None, height=1280, width=720):
        # capture already open?
        if self.capture:
            if self.capture.isOpened():
                print("capture already open")
                return
            self.capture = None

        # experimental:
        if device == 'stream':
            self.capture = cv2.VideoCapture()
            # open network stream (in this case IP camera app on android
            self.capture.open("http://192.168.0.59:8080/video")
        elif device is None:
            device = self.device
            # open hardware connected device
            self.capture = cv2.VideoCapture(device)
        if not self.capture.isOpened:
            print("Error accessing camera!")
            return 0
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        # self.capture.set(cv2.CAP_PROP_BRIGHTNESS, 0.01)
        # TODO: correct for lighting conditions?

    # method to return calibrated frame
    def pull_cal_frame(self, src=None):
        if src is None:
            has_frame, src = self.capture.read()
            if not has_frame:
                print("Error taking picture")
                return 0
        if not self.calibration:
            print("Error: no calibration data")
            return 0
        # use calibration parameters to generate calibrated image
        # alternative: use warpPerspective (https://www.programcreek.com/python/example/84096/cv2.undistort)
        # or remap
        # (https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html)
        src = cv2.undistort(src, self.calibration['mtx'], self.calibration['dist'], None, self.calibration['new_mtx'])
        # use region of interest for cropping (roi don't make much sense currently)
        # x, y, w, h = self.calibration['roi']
        # src = src[y:y+h, x:x+w]
        return src

    # method to return a frame
    def pull_frame(self, calibrated_if_available=False):
        has_frame, src = self.capture.read()
        if not has_frame:
            print("Error taking picture")
            return 0
        if calibrated_if_available and self.calibration:
            d = dict()
            d['src'] = src
            d['calibrated'] = self.pull_cal_frame(src)
            return d
        else:
            return src

    # method to end capture
    def stop_capture(self):
        self.capture.release()
        self.capture = None

    # helper for video capture testing
    def show_video(self):
        print("camera preview, 'q' to continue, ESC to quit")
        fps = 30
        self.prepare_capture()
        while True:
            img = self.pull_frame()
            cv2.imshow("img", img)
            key = cv2.waitKey(int(1000 / fps)) & 0xFF
            if key == ord('q'):
                break
            elif key == 27:
                exit(0)
        self.stop_capture()
        cv2.destroyAllWindows()
