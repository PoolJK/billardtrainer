from queue import Queue
from threading import Thread

from .utils import *
from .ball import Ball


class Detection:

    def __init__(self, camera, beamer, queue_size):
        self.camera = camera
        self.beamer = beamer
        self.output_q = Queue(queue_size)
        self.stopped = False

    def queue(self, index, image):
        t = Thread(target=self.detect, args=[index, image])
        t.daemon = True
        t.start()

    def detect(self, index, image):
        if not self.stopped:
            t0 = now()
            debug('detection: index: {}: started'.format(index), settings.DEBUG)
            if settings.debug and settings.show_table:
                scale = max(cv2.getTrackbarPos('scale', 'beamer') / 10, 0.1)
                grad_val = max(cv2.getTrackbarPos('grad_val', 'beamer') * scale, 1)
                acc_thr = max(cv2.getTrackbarPos('acc_thr', 'beamer') * scale, 1)
                dp = max(cv2.getTrackbarPos('dp', 'beamer') * scale, 1)
                min_dist = max(cv2.getTrackbarPos('min_dist', 'beamer') * scale, 1)
                min_radius = int(cv2.getTrackbarPos('min_radius', 'beamer') * scale)
                max_radius = int(cv2.getTrackbarPos('max_radius', 'beamer') * scale)
                balls = Ball.find(grad_val, acc_thr, dp, min_dist, min_radius,
                                  max_radius, scale, image, self.camera.offset_x, self.camera.offset_y,
                                  self.camera.ppm_x, self.camera.ppm_y)
            else:
                balls = Ball.find(Ball.grad_val, Ball.acc_thr, Ball.dp, Ball.min_dist, Ball.min_radius, Ball.max_radius,
                                  1, image, self.camera.offset_x, self.camera.offset_y, self.camera.ppm_x,
                                  self.camera.ppm_y)
            if balls is not None:
                self.output_q.put([index, image, balls])
            d = dt(t0, now())
            debug('detection: index: {}: {:3d}ms   {} balls added'
                  .format(index, d, len(balls) if balls is not None else 0), settings.TIMING)

    def stop(self):
        self.stopped = True
