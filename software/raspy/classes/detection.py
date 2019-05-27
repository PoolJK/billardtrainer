import queue
from queue import Queue
from threading import Thread

from . import settings
from .utils import *
from .ball import Ball
from .camera import Camera


class Detection:

    def __init__(self, camera):
        self.camera = camera
        self.t = Thread(target=self.detect, args=())
        self.t.daemon = True
        self.msgQ = Queue(1)
        self.image = None
        self.pause_ms = 0

    def start(self):
        self.t.start()

    def pause(self, ms):
        self.pause_ms = ms

    def detect(self):
        while True:
            wait(self.pause_ms)
            self.pause_ms = 0
            t0 = now()
            self.image = self.camera.get_image()
            # do some stuff then add a message to the queue if anything is found
            balls = Ball.find(self.image, self.camera.offset_x, self.camera.offset_y,
                              self.camera.ppm_x, self.camera.ppm_y)
            if balls is not None:
                self.msgQ.put(balls)
                # print('balls added to Detection Queue')
            d = dt(t0, now())
            if settings.debug:
                print('detection thread loop time: {:3d}'.format(d))

    def read(self):
        try:
            return self.msgQ.get_nowait()
        except queue.Empty:
            return None
