from .visual_item import VisualItem
from ..utils import *


class Line(VisualItem):
    def __init__(self, x1, y1, x2, y2, color=None):
        super().__init__(x1, y1, color)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw_self(self, image, offset_x, offset_y, ppm_x, ppm_y):
        screen_p1 = (int((self.x1 - offset_x) * ppm_x), int((self.y1 - offset_y) * ppm_y))
        screen_p2 = (int((self.x2 - offset_x) * ppm_x), int((self.y2 - offset_y) * ppm_y))
        cv2.line(image, screen_p1, screen_p2, self.color)
        pass

    @staticmethod
    def find_self():
        return super().find_self()
