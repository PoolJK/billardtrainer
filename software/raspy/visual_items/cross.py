from software.raspy.visual_items.visual_item import VisualItem
import cv2


class Cross(VisualItem):

    def __init__(self, x, y, length, color=None):
        if color is None:
            color = (255, 255, 255)
        super().__init__(x, y, color)
        self.length = length

    def draw_self(self, image, pix_per_mm, offset_x, offset_y):
        cv2.drawMarker(image, (int((self.x + offset_x) * pix_per_mm), int((self.y + offset_y) * pix_per_mm)),
                       self.color, cv2.MARKER_CROSS, int(self.length * pix_per_mm), 1)

    def find_self(self, image):
        return super().find_self(image)
