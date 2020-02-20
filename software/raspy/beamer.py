import cv2
import numpy as np
from software.raspy.visual_items.ball import Ball
from software.raspy.visual_items.table import Table
from software.raspy.settings import Settings



class Beamer:
    """
    A projector class for showing image on table.
    Needs to take offset and distance in account to correct displayed image.
    """

    def __init__(self, resolution_x=1280, resolution_y=720, pix_per_mm=206/170):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.pix_per_mm = pix_per_mm
        #: x offset of beamer from table mid point in mm
        self.offset_x = 1000
        #: y offset of beamer from table mid point in mm
        self.offset_y = -100
        #: objects to show in image
        self.objects = []
        # create black image to show objects in
        self.outPict = np.zeros((self.resolution_y, self.resolution_x, 3 ), np.uint8)
        self.outPict[:] = (0, 0, 0)
        # create image for output on raspi's hdmi output
        #self.hdmiPict = np.zeros((768, 1024, 3), np.uint8)
        #print(self.hdmiPict.shape)
        # create window for beamer output (height, width, dimension for numpy array)
        if  Settings.on_raspy:
            cv2.namedWindow("beamer", cv2.WINDOW_AUTOSIZE + cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.namedWindow("beamer")


    def show_objects(self):
        for obj in self.objects:
            obj.draw_self(self.outPict, self.pix_per_mm, self.offset_x, self.offset_y)
        if Settings.debugging:
            cv2.drawMarker(self.outPict, (int(self.outPict.shape[1] / 2),
                                          int(self.outPict.shape[0] / 2)),
                           (0, 165, 255), cv2.MARKER_CROSS, int(self.outPict.shape[1]), 2)
        cv2.imshow("beamer", self.outPict)


    def show_image(self, image) -> None:
        """
        Show some image on beamer.
        :param image: Array with image to show
        """
        cv2.imshow("beamer", image)


    def show_white(self):
        # create black image to show objects in
        whitePict = np.zeros((self.resolution_y, self.resolution_x, 3), np.uint8)
        whitePict[:] = (255, 255, 255)
        cv2.imshow("beamer", whitePict)


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
