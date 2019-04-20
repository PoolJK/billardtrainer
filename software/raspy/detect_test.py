#!/usr/bin/python3

import os
import time
import cv2
import numpy as np

from classes.ball import Ball
from classes.camera import Camera
from classes.beamer import Beamer


class DetectTest:

    x_scale = 0
    y_scale = 0
    camera = None
    beamer = None
    debug = False

    def __init__(self, args):
        if args.debug:
            self.debug = True
        # get source resolution:
        if args.sres:
            x, y = 0, 0
            if ',' in args.sres:
                x, y = args.dres.split(',')
            elif 'x' in args.sres:
                x, y = args.sres.split('x')
            else:
                print('bad resolution format, use 1280,720 or 1280x720')
                exit(0)
            self.src_size = (int(x), int(y))
        else:
            self.src_size = None
        # get display resolution
        if args.dres:
            x, y = 0, 0
            if ',' in args.dres:
                x, y = args.dres.split(',')
            elif 'x' in args.dres:
                x, y = args.dres.split('x')
            else:
                print('bad resolution format, use 1280,720 or 1280x720')
                exit(0)
            self.win_size = (int(x), int(y))
        else:
            self.win_size = self.src_size
        # set up camera
        self.camera = Camera(args, self.src_size, self.win_size)
        # offset to other monitor
        self.beamer = Beamer(args, self.win_size, (1920, 0))
        # preview is started in Camera, so don't start anything afterwards
        if not args.preview:
            # run calibration per flag
            if args.calibrate:
                self.camera.auto_calibrate(self.beamer, args.cal_filename)
            else:
                # run manual if not loaded
                if not self.camera.is_calibrated:
                    self.camera.manual_calibrate(self.beamer)

    def main(self):
        self.camera.show_preview(self.camera.device)
        exit(0)
        print('\nstarting detection test{}, \'x\' to quit, \'s\' to save output frame'
              .format(' in debug mode' if self.debug else ''))
        self.camera.prepare_capture()
        cv2.namedWindow('out', cv2.WINDOW_NORMAL)
        self.beamer.window('beamer_out', cv2.WINDOW_NORMAL)
        # cv2.namedWindow('hsv_mask', cv2.WINDOW_NORMAL)
        # cv2.namedWindow('hsv', cv2.WINDOW_NORMAL)
        # cv2.namedWindow('src', cv2.WINDOW_NORMAL)
        # cv2.setMouseCallback('src', self.mouse_callback)
        cv2.createTrackbar('grad_val', 'out', 27, 255, self.nothing)
        cv2.createTrackbar('acc_thr', 'out', 48, 255, self.nothing)
        cv2.createTrackbar('min_dist', 'out', 28, 255, self.nothing)
        cv2.createTrackbar('dp', 'out', 2, 255, self.nothing)
        cv2.createTrackbar('min_radius', 'out', 11, 255, self.nothing)
        cv2.createTrackbar('max_radius', 'out', 19, 255, self.nothing)
        #cv2.createTrackbar('h_lower', 'hsv_mask', 0, 255, self.nothing)
        #cv2.createTrackbar('s_lower', 'hsv_mask', 0, 255, self.nothing)
        #cv2.createTrackbar('v_lower', 'hsv_mask', 0, 255, self.nothing)
        #cv2.createTrackbar('h_upper', 'hsv_mask', 255, 255, self.nothing)
        #cv2.createTrackbar('s_upper', 'hsv_mask', 255, 255, self.nothing)
        #cv2.createTrackbar('v_upper', 'hsv_mask', 255, 255, self.nothing)
        while True:
            start = now()

            # read source
            xsrc, src = self.camera.pull_cal_frame()
            if src is None:
                print('error in main: couldn\'t read from src')
                return 0
            t1 = now()

            gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)
            #hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
            #lower = np.array([cv2.getTrackbarPos('h_lower', 'hsv_mask'), cv2.getTrackbarPos('s_lower', 'hsv_mask'),
            #                  cv2.getTrackbarPos('v_lower', 'hsv_mask')])
            #upper = np.array([cv2.getTrackbarPos('h_upper', 'hsv_mask'), cv2.getTrackbarPos('s_upper', 'hsv_mask'),
            #                  cv2.getTrackbarPos('v_upper', 'hsv_mask')])
            # Threshold the HSV image
            #mask = cv2.inRange(hsv, lower, upper)
            # Bitwise-AND mask and original image
            #gray_masked = cv2.bitwise_and(gray, gray, mask=mask)
            # get parameters for hough_circle detection
            grad_val = max(cv2.getTrackbarPos('grad_val', 'out'), 1)
            acc_thr = max(cv2.getTrackbarPos('acc_thr', 'out'), 1)
            dp = max(cv2.getTrackbarPos('dp', 'out'), 1)
            min_dist = max(cv2.getTrackbarPos('min_dist', 'out'), 1)
            min_radius = cv2.getTrackbarPos('min_radius', 'out')
            max_radius = cv2.getTrackbarPos('max_radius', 'out')
            t2 = now()

            # run detection
            found_balls = Ball.find(gray, dp, min_dist, grad_val, acc_thr, min_radius, max_radius)
            t3 = now()

            # create output
            out = np.zeros(gray.shape, np.uint8)
            for ball in found_balls:
                ball.draw(out)
            # overlay contours over source image
            out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
            out = cv2.addWeighted(src, 1, out, 1, 0)
            t4 = now()

            # display (and resize) all windows
            cv2.imshow('xsrc', cv2.resize(xsrc, self.win_size))
            # cv2.imshow('src', cv2.resize(src, self.win_size, cv2.INTER_CUBIC))
            #cv2.imshow('hsv_mask', cv2.resize(mask, self.win_size, cv2.INTER_CUBIC))
            #cv2.setMouseCallback('hsv', self.mouse_callback)
            #cv2.imshow('hsv', cv2.resize(hsv, self.win_size, cv2.INTER_CUBIC))
            cv2.imshow('out', cv2.resize(out, self.win_size, cv2.INTER_CUBIC))
            self.beamer.show('beamer_out', cv2.resize(out, (self.beamer.height, self.beamer.width)), fullscreen=True)
            # cv2.resizeWindow('hsv_mask', self.win_size[0], self.win_size[1])
            # cv2.resizeWindow('out', self.win_size[0], self.win_size[1])
            # cv2.resizeWindow('hsv', self.win_size[0], self.win_size[1])
            t5 = now()
            if self.debug:
                print('\rmain loop: {: 5d}ms, t1={: 5d}ms t2={: 5d}ms t3={: 5d}ms t4={: 5d}ms'
                      .format(dt(t4, t5), dt(start, t1), dt(t1, t2), dt(t2, t3), dt(t3, t4)), end='')
            key = cv2.waitKey(1) & 0xFF
            if key == ord('x'):
                print('')
                break
            if key == ord('s'):
                # save current frame to disk
                print('\nsaving current src and out to file')
                c = 0
                path = 'resources/experimental/outputs'
                if not os.path.isdir(path):
                    os.makedirs(path)
                while os.path.isfile(path + '/out{:02d}.jpg'.format(c)):
                    c += 1
                cv2.imwrite(path + '/out{:02d}.jpg'.format(c), out)
                cv2.imwrite(path + '/in{:02d}.jpg'.format(c), xsrc)
            if key == 27:
                # ESC = exit
                print('bye')
                self.camera.stop_capture()
                cv2.destroyAllWindows()
                exit(0)
        self.camera.stop_capture()
        cv2.destroyAllWindows()
        return 0

    def mouse_callback(self, event, x, y, flags, param):
        # on left mouse clock, print coordinates
        if self == cv2.EVENT_LBUTTONDOWN:
            print("Coord image: {} {}".format(x, y))

    # empty method as callback for Trackbars
    def nothing(*x):
        pass


def dt(t1, t2):
    # time difference as int in [ms]
    return int((t2 - t1) * 1000)


def now():
    # current time
    return time.time()
