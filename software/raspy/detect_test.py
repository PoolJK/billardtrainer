#!/usr/bin/python3

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
        # set up beamer (offset to use monitor on the right)
        self.beamer = Beamer(args, self.win_size, (1920, 0))
        if args.calibrate:
            # run calibration per flag
            self.camera.auto_calibrate(self.beamer, args.cal_filename)
        if args.preview:
            self.camera.show_preview()

    def main(self):
        self.camera.show_preview(fullscreen=True)
        # exit(0)
        # print('\nstarting detection test{}, \'x\' to quit'.format(' in debug mode' if self.debug else ''))
        cv2.destroyAllWindows()
        return 0
