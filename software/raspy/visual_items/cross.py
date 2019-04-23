from software.raspy.visual_items.visual_item import VisualItem
import cv2


class Cross(VisualItem):
    def __init__(self, x, y, length):
        super().__init__(x,y, (255, 255, 255))
        self.length = length

    def draw_self(self, image, pix_per_mm, offs_x, offs_y) -> None:
        cv2.drawMarker(image, (int((self.x + offs_x) * pix_per_mm), int((self.y + offs_y) * pix_per_mm)),
                       self.color, cv2.MARKER_CROSS, int(self.length * pix_per_mm), 1)
