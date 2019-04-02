# the camera wants a class too :'-/

import cv2
# import numpy as np


class Camera:

    capture = None
    calibration_parameters = None

    def __init__(self):
        pass

    # method to calibrate optical parameters
    # takes number of calibration images with different patterns / angles
    # returns correction matrix or some crap

    def calibrate(self):
        # take pictures
        # calculate something
        self.calibration_parameters = 2
        return self.calibration_parameters

    # method to prepare capture
    def prepare_capture(self, device, height=1280, width=720):
        self.capture = cv2.VideoCapture(device)
        if not self.capture.isOpened:
            print("Error accessing camera!")
            return 0
        # doesn't work with my camera)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # method to return a frame
    def pull_frame(self):
        has_frame, src = self.capture.read()
        if not has_frame:
            print("Error taking picture")
            return 0
        if not self.calibration_parameters:
            print("camera not calibrated")
            return src
        else:
            d = dict()
            d['src'] = src
            d['calibrated'] = src * self.calibration_parameters
            return d

    # method to end capture
    def stop_capture(self):
        self.capture.release()
