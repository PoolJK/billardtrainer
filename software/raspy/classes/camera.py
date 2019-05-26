import queue
from queue import Queue
from threading import Thread

from .utils import *

try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ModuleNotFoundError:
    pass


class Camera:
    resolution = (1920, 1088)

    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = self.resolution
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
        self.rawCapture = PiRGBArray(self.camera, size=self.resolution)
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True
        self.Q = Queue(1)
        wait(100)
        self.t.start()

    def update(self):
        for frame in self.camera.capture_continuous(self.rawCapture, format="bgr",
                                                    use_video_port=True):
            frame.array = rotate(frame.array, 180)
            self.Q.put(frame.array)
            self.rawCapture.truncate(0)

    def get_image(self):
        try:
            return self.Q.get_nowait()
        except queue.Empty:
            return None
