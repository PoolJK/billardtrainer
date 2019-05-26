#!/usr/bin/python3

from .classes.utils import *
from .classes.beamer import Beamer
from .classes.camera import Camera
from .classes.table_sim import TableSim
from .classes.detection import Detection


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
        self.camera = Camera()
        # set up beamer (offset to use monitor on the right)
        self.beamer = Beamer()
        self.detection = Detection(self.camera)
        # if args.calibrate:
        #     # run calibration per flag
        #     self.camera.auto_calibrate(self.beamer, args.cal_filename)
        # if args.preview:
        #     self.camera.show_preview()

    def main(self):
        # self.camera.show_preview(fullscreen=True)
        table_sim = TableSim()
        table_sim.start()
        """
        cv2.namedWindow('camera', cv2.WINDOW_NORMAL)
        cv2.moveWindow('camera', 0, 0)
        self.beamer.show_white()
        self.detection.start()
        i = 0
        while True:
            t0 = now()
            msg = self.detection.read()
            if msg is not None:
                print(msg)
            image = self.detection.get_image()
            if image is not None:
                print('resources/detection_input/img{:02}.jpg'.format(i))
                cv2.imwrite('./resources/detection_input/img{:02}.jpg'.format(i), image)
                i = i + 1
                cv2.imshow('camera', image)
                cv2.resizeWindow('camera', 640, 360)
            print('loop time: {: 4d}ms'.format(dt(t0, now())), end='\r')
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
        # exit(0)
        cv2.destroyAllWindows()
        return 0
        """
