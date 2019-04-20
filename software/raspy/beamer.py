import cv2
import numpy as np
from software.raspy.ball import Ball
from software.raspy.settings import Settings

beam_zoom = 11.8

class Beamer:
    """
    A projector class for showing image on table.
    Needs to take offset and distance in account to correct displayed image.
    """

    def __init__(self, resolution_x=1280, resolution_y=720):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        #: x offset of beamer from table mid point in mm
        self.offset_x = 0
        #: y offset of beamer from table mid point in mm
        self.offset_y = 0
        #: objects to show in image
        self.objects = []
        # create black image to show found artefacts in
        self.outPict = np.zeros((self.resolution_y, self.resolution_x, 3 ), np.uint8)
        self.outPict[:] = (0, 0, 0)
        # create window for beamer output (height, width, dimension for numpy array)
        if  Settings.on_raspy:
            cv2.namedWindow("beamer", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.namedWindow("beamer")


    def show_objects(self):
        for obj in self.objects:
            obj.draw_self(self.outPict)

        cv2.imshow("beamer", self.outPict)


    def show_image(self, image):
        cv2.imshow("beamer", image)


    def clear_image(self):
        self.objects.clear()


    def close_window(self):
        cv2.destroyWindow("beamer")


    def add_object(self, object):
        if type(object) is Ball:
            object.x = object.x * beam_zoom
            object.y = object.y * beam_zoom
            object.radius = object.radius * beam_zoom
        self.objects.append(object)
