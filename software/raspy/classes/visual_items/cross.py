from .visual_item import VisualItem
from .. import settings
import cv2


class Cross(VisualItem):

    def __init__(self, x, y, length):
        super().__init__(x, y, (255, 255, 255))
        self.length = length

    def draw_self(self, image, offset_x, offset_y, ppm_x, ppm_y):
        screen_x = int((self.x - offset_x) * ppm_x)
        screen_y = int((self.y - offset_y) * ppm_y)
        if settings.debug:
            print("cross drawn at: ({}, {}) [px] ({}, {}) [mm]".format(screen_x, screen_y, self.x, self.y))
        cv2.drawMarker(image, (screen_x, screen_y),
                       self.color, cv2.MARKER_CROSS, int(self.length * ppm_x), 5)

    @staticmethod
    def find_self(**kwargs):
        pass
