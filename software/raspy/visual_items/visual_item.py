
class VisualItem:
    """ Base class for all items to be displayed on table"""
    def __init__(self, x, y, color=[33, 55, 77]):
        """
        Generate new visual item
        :param x: x-position of center in mm
        :param y: y-position of center in mm
        :param color: color of item
        """
        self.x = x
        self.y = y
        self.color = color


    def draw_self(self, image, pix_per_mm, offs_x, offs_y) -> None:
        """
        Draw self in image.
        :param pix_offs_x: offset of zero position in mm
        :param pix_offs_y: offset of zero position in mm
        :param pix_per_mm: resolution in pixel per mm
        :param image: Array with image to draw on
        """
        raise NotImplementedError


    def find_self(self, image) -> 'VisualItem':
        """
        Find own contour in existing table image
        :param image: image of table
        :return: Found items of self
        """
        raise NotImplementedError