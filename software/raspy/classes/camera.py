import os
from queue import Queue
from threading import Thread

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
        self.output_q = Queue(10)
        debug('camera offset(x,y)=({:.2f}, {:.2f}) ppmx={:.2f} ppmy={:.2f}'.format(
            self.offset_x, self.offset_y, self.ppm_x, self.ppm_y), 0)
        if settings.on_pi:
            self.camera = PiCamera()
            self.camera.resolution = (self.resolution_x, self.resolution_y)
            self.camera.framerate = 25
            # self.camera.iso = 800
            # Wait for the automatic gain control to settle
            wait(1000)
            # Now fix the values
            self.camera.shutter_speed = self.camera.exposure_speed
            self.camera.exposure_mode = 'off'
            g = self.camera.awb_gains
            self.camera.awb_mode = 'off'
            self.camera.awb_gains = g
            self.rawCapture = PiRGBArray(self.camera, size=(self.resolution_x, self.resolution_y))
        self.stopped = False
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True
        self.t.start()

    def update(self):
        # development @home: read images from resources/detection_input instead of camera
        path = 'resources/experimental/detection_input'
        if settings.on_pi and not settings.simulate:
            for frame in self.camera.capture_continuous(self.rawCapture, format="bgr",
                                                        use_video_port=True):
                if self.stopped:
                    exit(0)
                t0 = now()
                frame.array = rotate(frame.array, -self.rotation)
                self.output_q.put(frame.array)
                self.rawCapture.truncate(0)
                t_src = dt(t0, now())
                if settings.debug:
                    debug('camera: queued src in {:2d}ms'.format(t_src), 0)
                    # i = 0
                    # while os.path.isfile('{}/img{:02}.jpg'.format(path, i)):
                    #     i += 1
                    # cv2.imwrite('{}/img{:02}.jpg'.format(path, i), frame.array)
                    # i += 1
        else:
            files = os.listdir(path)
            while True:
                if self.stopped:
                    exit(0)
                for file in files:
                    t0 = now()
                    self.output_q.put(cv2.imread('{}/{}'.format(path, file)))
                    debug('camera: queued {}/{} in {:2d}ms'.format(path, file, dt(t0, now())), 0)

    def stop(self):
        self.stopped = True
        wait(100)
