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
    def __init__(self, resolution_x=1920, resolution_y=1088, offset_x=0, offset_y=0, ppm_x=1, ppm_y=1, rotation=90):
        self.resolution_x = resolution_x
        self.offset_x = offset_x
        self.ppm_x = ppm_x
        self.resolution_y = resolution_y
        self.offset_y = offset_y
        self.ppm_y = ppm_y
        self.rotation = rotation
        self.image = None

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
            for frame in self.camera.capture_continuous(self.rawCapture, format="bgr",
                                                        use_video_port=True):
                frame.array = rotate(frame.array, 90)
                self.Q.put(frame.array)
                self.rawCapture.truncate(0)
        else:
            i = 36
            while True:
                # print(os.path.abspath(''))
                self.Q.put(rotate(cv2.imread('resources/experimental/detection_input/img{:02}.jpg'.format(i)),
                                  self.rotation))
                i = i + 1
                if i == 39:
                    i = 4

    def get_image(self):
        # TODO idea: also return a timestamp for synchronization of visual_items across beamer, detection and bluetooth
        self.image = self.Q.get()
        return self.image
