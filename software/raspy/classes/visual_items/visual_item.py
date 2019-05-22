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

    def draw_self(self, image, offs_x, offs_y, ppm_x, ppm_y):
        """
        Draw self in image.
        :param image: Array with image to draw on
        :param ppm_x: beamer resolution in pixel per mm
        :param ppm_y: beamer resolution in pixel per mm
        :param offs_x: beamer x position offset relative to table mid point in mm
        :param offs_y: beamer y position offset relative to table mid point in mm
        """
        raise NotImplementedError

    @staticmethod
    def find_self(**kwargs):
        """
        Find own contour in existing table image
        :return: Found items of self
        """
        raise NotImplementedError