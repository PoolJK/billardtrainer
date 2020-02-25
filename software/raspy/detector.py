import sys
import cv2
import time
import settings
from visual_items.table import Table
from visual_items.ball import Ball


def mouse_callback(event, x, y, flags, param):
    """
    print coordinates of mouse on click
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Coord: {} {}".format(x, y))


class TakeImage(Exception):
    def __init__(self, msg):
        print(msg)
        # cv2.destroyAllWindows()
        sys.exit(-1)


class Detector:
    def __init__(self, semaphore, cam, filename):
        self.objects = []
        self.src = []
        self.camera = cam
        self.isrunning = True
        self.sema = semaphore
        if filename is not None:
            self.src = cv2.imread(filename, cv2.IMREAD_COLOR)
            # Check if image is loaded fine
            if self.src is None:
                raise TakeImage('Error loading image file!')
        if settings.debugging is True:
            cv2.namedWindow("source", cv2.WINDOW_NORMAL)
            cv2.imshow("source", self.src)
            # attach mouse callback to window for measuring
            cv2.setMouseCallback("source", mouse_callback)


    def run(self):
        while self.isrunning:
            self.sema.acquire()
            if self.camera is not None:
                self.src = self.camera.take_picture()
                if self.src is None:
                    raise TakeImage('Error taking picture!')
            # find table
            found_table = Table.find_self(self.src, settings.camera_pix_per_mm,
                                          settings.camera_offset_x, settings.camera_offset_y)
            self.objects.append(found_table)
            # find balls
            found_balls = Ball.find_self(self.src, settings.camera_pix_per_mm,
                                         settings.camera_offset_x, settings.camera_offset_y)
            for ball in found_balls:
                self.objects.append(ball)

            #time.sleep(0.1)


    def get_objects(self):
        self.sema.release()
        return self.objects


    def stop(self):
        self.isrunning = False