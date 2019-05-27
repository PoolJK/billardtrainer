import os
from queue import Queue
from threading import Thread

from . import settings
from .utils import *

try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ModuleNotFoundError:
    pass


class Camera:
    def __init__(self, resolution_x=1088, resolution_y=1920, offset_x=0, offset_y=0, ppm_x=1, ppm_y=1, rotation=90):
        self.resolution_x = resolution_x
        self.offset_x = offset_x
        self.ppm_x = ppm_x
        self.resolution_y = resolution_y
        self.offset_y = offset_y
        self.ppm_y = ppm_y
        self.rotation = rotation
        self.image = None
        print('camera offset(x,y)=({:.2f}, {:.2f}) ppmx={:.2f} ppmy={:.2f}'.format(
            self.offset_x, self.offset_y, self.ppm_x, self.ppm_y))

        if settings.on_pi:
            self.camera = PiCamera()
            self.camera.resolution = (self.resolution_x, self.resolution_y)
            self.camera.framerate = 25
            self.camera.iso = 400
            # Wait for the automatic gain control to settle
            wait(1000)
            # Now fix the values
            self.camera.shutter_speed = self.camera.exposure_speed
            self.camera.exposure_mode = 'off'
            g = self.camera.awb_gains
            self.camera.awb_mode = 'off'
            self.camera.awb_gains = g
            self.rawCapture = PiRGBArray(self.camera, size=(self.resolution_x, self.resolution_y))
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True
        self.Q = Queue(1)
        self.t.start()

    def update(self):
        # development @home: read images from resources/detection_input instead of camera
        if settings.on_pi:
            i = 0
            for frame in self.camera.capture_continuous(self.rawCapture, format="bgr",
                                                        use_video_port=True):
                frame.array = rotate(frame.array, -self.rotation)
                self.Q.put(frame.array)
                self.rawCapture.truncate(0)
                if settings.debug:
                    print(os.path.abspath('./resources/experimental/detection_input'))
                    cv2.imwrite('./resources/experimental/detection_input/img{:02}.jpg'.format(i), frame.array)
                    i = i + 1
        else:
            i = 4
            while True:
                # print(os.path.abspath(''))
                if i < 8:
                    self.Q.put(cv2.imread('resources/experimental/detection_input/img{:02}.jpg'.format(i)))
                else:
                    self.Q.put(rotate(cv2.imread('resources/experimental/detection_input/img{:02}.jpg'.format(i)),
                                      self.rotation))
                i = i + 1
                if i == 39:
                    i = 4

    def get_image(self):
        # TODO idea: also return a timestamp for synchronization of visual_items across beamer, detection and bluetooth
        self.image = self.Q.get()
        return self.image
