from software.raspy.visual_items.visual_item import VisualItem
import cv2


class Rectangle(VisualItem):

    def __init__(self, x, y, width, height, angle=0, color=None):
        if color is None:
            color = (255, 255, 255)
        super().__init__(x, y, color)
        self.width = width
        self.height = height
        self.angle = angle

    def draw_self(self, image, pix_per_mm, offset_x, offset_y):
        cv2.rectangle(image, (
            int((self.x + offset_x) * pix_per_mm),
            int((self.y + offset_y) * pix_per_mm)),
                (int(((self.x + offset_x) + self.width) * pix_per_mm),
                 int(((self.y + offset_y) + self.height) * pix_per_mm)),
                self.color, 1, )

    def find_self(self, image):
        return super().find_self(image)
