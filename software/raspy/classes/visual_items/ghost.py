from .ball import Ball
from ..utils import *


class Ghost(Ball):
    def __init__(self, x, y, radius=26, color=None):
        super().__init__(x, y, radius, color)

    def draw_self(self, image, offset_x, offset_y, ppm_x, ppm_y):
        screen_x = int((self.x - offset_x) * ppm_x)
        screen_y = int((self.y - offset_y) * ppm_y)
        cv2.circle(image, (screen_x, screen_y),
                   int(self.radius * ppm_x), self.color, 5)
        pass

    @staticmethod
    def find_self(**kwargs):
        return super().find_self(kwargs)
