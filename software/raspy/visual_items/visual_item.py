
class VisualItem:
    """ Base class for all items to be displayed on table"""
    def __init__(self, x, y, color=[33, 55, 77]):
        """
        Generate new visual item
        :param x: x-position of center in mm from table mid point
        :param y: y-position of center in mm from table mid point
        :param color: color of item
        """
        self.x = x
        self.y = y
        self.color = color


    def draw_self(self, image, pix_per_mm, offs_x, offs_y) -> None:
        """
        Draw self in image.
        :param pix_offs_x: beamer x position offset relative to table mid point in mm
        :param pix_offs_y: beamer y position offset relative to table mid point in mm
        :param pix_per_mm: beamer resolution in pixel per mm
        :param image: Array with image to draw on
        """
        raise NotImplementedError


    @staticmethod
    def find_self(image, pix_per_mm, offs_x, offs_y):
        """
        Find own contour in existing table image
        :param pix_per_mm:
        :param offs_x: camera x position offset relative to table mid point in mm
        :param offs_y: camera y position offset relative to table mid point in mm
        :param image: image of table
        :return: Found items of self
        """
        raise NotImplementedError