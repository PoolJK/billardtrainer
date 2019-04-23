import cv2
import numpy as np
from software.raspy.settings import Settings


class Beamer:
    """
    A projector class for showing image on table.
    Needs to take offset and distance in account to correct displayed image.
    """

    def __init__(self, resolution_x=1280, resolution_y=720, pix_pro_mm=200 / 150):
        self.zoom = 12
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
        self.visual_items = []
        # create black image to show found artefacts in
        self.outPict = np.zeros((self.resolution_y, self.resolution_x, 3), np.uint8)
        if Settings.on_raspy:
            cv2.namedWindow("beamer", cv2.WINDOW_AUTOSIZE + cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.namedWindow("beamer")

    def show_visual_items(self):
        for obj in self.visual_items:
            obj.draw_self(self.outPict, self.pix_pro_mm, self.offset_x, self.offset_y)
        # cv2.imwrite("beamtest.jpg", self.outPict)
        # self.hdmiPict = cv2.resize(self.outPict, (self.hdmiPict.shape[1], self.hdmiPict.shape[0]),
        #                         1.2, 0, cv2.INTER_AREA)
        # cv2.imwrite("ball2_dect_hdmi.jpg", self.hdmiPict)
        cv2.imshow("beamer", self.outPict)

    @staticmethod
    def show_image(image):
        cv2.imshow("beamer", image)

    def clear_image(self):
        self.visual_items.clear()
        self.outPict = np.zeros((self.resolution_y, self.resolution_x, 3), np.uint8)
        self.show_visual_items()

    @staticmethod
    def close_window():
        cv2.destroyWindow("beamer")

    def add_visual_item(self, visual_item):
        # object.x -= (1280 - 1024) / pict_pix_per_mm
        # object.y -= (960 - 768) / pict_pix_per_mm
        # object.x *= beam_zoom
        # object.y *= beam_zoom
        # if isinstance(object, Ball):
        #     object.radius = object.radius * beam_zoom
        # elif isinstance(object, Table):
        #     object.w *= beam_zoom
        #     object.h *= beam_zoom

        self.visual_items.append(visual_item)
