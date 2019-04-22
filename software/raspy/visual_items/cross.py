from software.raspy.visual_items.visual_item import VisualItem
import cv2


class Cross(VisualItem):
    def __init__(self, x, y, length):
        super().__init__(x,y, (255, 255, 255))
        self.length = length

    def draw_self(self, image) -> None:
        cv2.drawMarker(image, (int(self.x), int(self.y)), self.color, cv2.MARKER_CROSS,
                       self.length, 1)
