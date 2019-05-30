from threading import Thread

from .utils import *
from .ball import Ball


class Detection:

    def __init__(self, camera, beamer, output_q):
        self.camera = camera
        self.beamer = beamer
        self.output_q = output_q

    def queue(self, index, image):
        t = Thread(target=self.detect, args=[
            index, image,
        ])
        t.daemon = True
        t.start()

    def detect(self, index, image):
        t0 = now()
        # try smaller image for faster detection
        scale = 1
        tmp_size = (int(self.camera.resolution_y * scale), int(self.camera.resolution_x * scale))
        # debug('tmp_size={}'.format(tmp_size))
        image = cv2.resize(image, tmp_size, cv2.INTER_CUBIC)
        # do some stuff then add a message to the queue if anything is found
        balls = Ball.find(image, self.camera.offset_x, self.camera.offset_y,
                          self.camera.ppm_x, self.camera.ppm_y, scale)
        if balls is not None:
            self.output_q.put([index, balls])
        d = dt(t0, now())
        debug('detection: index: {}: {:3d}ms   {} balls added'.format(index, d, len(balls) if balls is not None else 0), settings.DEBUG)
