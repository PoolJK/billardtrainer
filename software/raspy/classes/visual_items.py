from .utils import *


class VisualItem:
    """ Base class for all items to be displayed on table"""

    def __init__(self, x, y, color=None):
        """
        Generate new visual item
        :param x: x-position of center in mm
        :param y: y-position of center in mm
        :param color: color of item
        """
        if color is None:
            color = [255, 255, 255]
        self.x = x
        self.y = y
        self.color = color

    def draw(self, image, offs_x, offs_y, ppm_x, ppm_y):
        pass

    @staticmethod
    def find(**kwargs):
        pass


class Line(VisualItem):
    def __init__(self, x, y, x2, y2, color=None):
        super().__init__(x, y, color)
        self.x2 = x2
        self.y2 = y2

    def draw(self, image, offset_x, offset_y, ppm_x, ppm_y):
        screen_p1 = (int((self.x - offset_x) * ppm_x), int((self.y - offset_y) * ppm_y))
        screen_p2 = (int((self.x2 - offset_x) * ppm_x), int((self.y2 - offset_y) * ppm_y))
        cv2.line(image, screen_p1, screen_p2, self.color, 5)
        pass

    @staticmethod
    def find():
        pass


class Cross(VisualItem):

    def __init__(self, x, y, length, color=None):
        if color is None:
            color = [255, 255, 255]
        super().__init__(x, y, color)
        self.length = length

    def draw(self, image, offset_x, offset_y, ppm_x, ppm_y):
        screen_x = int((self.x - offset_x) * ppm_x)
        screen_y = int((self.y - offset_y) * ppm_y)
        # print("cross drawn at: ({}, {}) [px] ({}, {}) [mm]".format(screen_x, screen_y, self.x, self.y))
        cv2.drawMarker(image, (screen_x, screen_y),
                       self.color, cv2.MARKER_CROSS, int(self.length * ppm_x), 5)

    @staticmethod
    def find():
        pass


class Ghost(VisualItem):
    def __init__(self, x, y, radius=26, color=None):
        super().__init__(x, y, color)
        self.radius = radius

    def draw(self, image, offset_x, offset_y, ppm_x, ppm_y):
        screen_x = int((self.x - offset_x) * ppm_x)
        screen_y = int((self.y - offset_y) * ppm_y)
        cv2.circle(image, (screen_x, screen_y),
                   int(self.radius * ppm_x), self.color, 5)
        pass

    @staticmethod
    def find():
        pass
