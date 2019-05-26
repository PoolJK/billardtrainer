import queue
from queue import Queue
from threading import Thread

from .camera import Camera
from .utils import *


class Detection:

    def __init__(self, camera):
        self.camera = camera
        self.t = Thread(target=self.detect, args=())
        self.t.daemon = True
        self.msgQ = Queue(1)
        self.imageQ = Queue(1)
        self.image = None
        wait(100)

    def start(self):
        self.t.start()

    def detect(self):
        while True:
            self.imageQ.put(self.camera.get_image())
            # do some stuff then add a message to the queue if anything is found
            # TODO when do I exit?

    def read(self):
        try:
            return self.msgQ.get_nowait()
        except queue.Empty:
            return None

    def get_image(self):
        try:
            self.image = self.imageQ.get(timeout=1)
        except queue.Empty:
            wait(100)
        if self.image is None:
            wait(100)
        return self.image
