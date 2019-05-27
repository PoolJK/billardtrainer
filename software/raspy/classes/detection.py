import queue
from queue import Queue
from threading import Thread

from .utils import *
from .ball import Ball


class Detection:

    def __init__(self, camera, beamer):
        self.camera = camera
        self.beamer = beamer
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
            # try smaller image for faster detection
            scale = 1
            tmp_size = (self.camera.resolution_y // scale, self.camera.resolution_x // scale)
            # debug('tmp_size={}'.format(tmp_size))
            image = cv2.resize(self.image, tmp_size, cv2.INTER_CUBIC)
            # do some stuff then add a message to the queue if anything is found
            balls = Ball.find(image, self.camera.offset_x, self.camera.offset_y,
                              self.camera.ppm_x, self.camera.ppm_y, scale)
            if balls is not None:
                self.msgQ.put(balls)
                debug('balls added to Detection Queue', 0)
            d = dt(t0, now())
            debug('detection thread loop time: {:3d} {}'.
                  format(d, '' if balls is None else '{} balls added'.format(len(balls))))

    def read(self):
        try:
            return self.msgQ.get_nowait()
        except queue.Empty:
            return None
