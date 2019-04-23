from software.raspy.visual_items.visual_item import VisualItem
import cv2


class Text(VisualItem):
    def __init__(self, x, y, text, color=None):
        if color is None:
            color = (255, 255, 255)
        super().__init__(x, y, color)
        self.text = text

    def draw_self(self, image, pix_per_mm, offset_x, offset_y):
        cv2.putText(image, self.text, (
            int((self.x + offset_x) * pix_per_mm),
            int((self.y + offset_y) * pix_per_mm)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.color, 1)

    def find_self(self, image):
        return super().find_self(image)
