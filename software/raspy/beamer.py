import cv2
import numpy as np
from software.raspy.camera import pict_pix_per_mm
from software.raspy.visual_items.ball import Ball
from software.raspy.visual_items.table import Table
from software.raspy.settings import Settings


beam_zoom = 12

class Beamer:
    """
    A projector class for showing image on table.
    Needs to take offset and distance in account to correct displayed image.
    """

    def __init__(self, resolution_x=1280, resolution_y=720, pix_pro_mm=200/150):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.pix_pro_mm = pix_pro_mm
        self.zero_x = (resolution_x / 2) / self.pix_pro_mm
        self.zero_y = (resolution_y / 2) / self.pix_pro_mm
        #: x offset of beamer from table mid point in mm
        self.offset_x = 0
        #: y offset of beamer from table mid point in mm
        self.offset_y = 0
        #: objects to show in image
        self.objects = []
        # create black image to show found artefacts in
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
            obj.draw_self(self.outPict, self.pix_pro_mm, self.zero_x, self.zero_y)
        # cv2.imwrite("beamtest.jpg", self.outPict)
        # self.hdmiPict = cv2.resize(self.outPict, (self.hdmiPict.shape[1], self.hdmiPict.shape[0]),
        #                         1.2, 0, cv2.INTER_AREA)
        # cv2.imwrite("ball2_dect_hdmi.jpg", self.hdmiPict)
        cv2.imshow("beamer", self.outPict)


    def show_image(self, image):
        cv2.imshow("beamer", image)


    def clear_image(self):
        self.objects.clear()


    def close_window(self):
        cv2.destroyWindow("beamer")


    def add_object(self, object):
        # object.x -= (1280 - 1024) / pict_pix_per_mm
        # object.y -= (960 - 768) / pict_pix_per_mm
        # object.x *= beam_zoom
        # object.y *= beam_zoom
        # if isinstance(object, Ball):
        #     object.radius = object.radius * beam_zoom
        # elif isinstance(object, Table):
        #     object.w *= beam_zoom
        #     object.h *= beam_zoom

        self.objects.append(object)
