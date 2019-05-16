import cv2
import numpy as np
from . import settings as settings


class Beamer:
    """
    A projector class for showing image on table.
    Needs to take offset and distance in account to correct displayed image.
    """

    def __init__(self, resolution_x=1280, resolution_y=720, pix_per_mm=206/150):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.pix_per_mm = pix_per_mm
        #: x offset of beamer from table mid point in mm
        self.offset_x = 0
        #: y offset of beamer from table mid point in mm
        self.offset_y = 0
        #: objects to show in image
        self.objects = []
        # create black image to show objects in
        self.outPict = np.zeros((self.resolution_y, self.resolution_x, 3 ), np.uint8)
        # create window for beamer output (height, width, dimension for numpy array)
        if settings.on_raspy:
            cv2.namedWindow("beamer", cv2.WINDOW_AUTOSIZE + cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.namedWindow("beamer")

    def show_objects(self):
        for obj in self.objects:
            obj.draw_self(self.outPict, self.pix_per_mm, self.offset_x, self.offset_y)
        if settings.debugging:
            cv2.drawMarker(self.outPict, (int(self.outPict.shape[1] / 2),
                                          int(self.outPict.shape[0] / 2)),
                           (0, 165, 255), cv2.MARKER_CROSS, int(self.outPict.shape[1]), 2)
        cv2.imshow("beamer", self.outPict)

    def get_image(self):
        """
        Get current outPict
        """
        return self.outPict

    def show_white(self):
        # create black image to show objects in
        white_pict = np.zeros((self.resolution_y, self.resolution_x, 3), np.uint8)
        white_pict[:] = (255, 255, 255)
        cv2.imshow("beamer", white_pict)

    def clear_image(self):
        self.objects.clear()
        cv2.imshow("beamer", self.outPict)

    def close_window(self):
        """
        Close full size window to show raspy desktop etc.
        """
        cv2.destroyWindow("beamer")

    def add_object(self, object):
        """
        Add object to show with show_objects()
        :param object:
        """
        self.objects.append(object)
