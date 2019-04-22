from software.raspy.visual_items.visual_item import VisualItem
import cv2


class Rectangle(VisualItem):
    def __init__(self, x, y, length):
        super().__init__(x,y, (255, 255, 255))
        self.length = length

    def draw_self(self, image, pix_per_mm, offs_x, offs_y) -> None:
        cv2.rectangle(image, (int((self.x + offs_x) * pix_per_mm), int((self.y + offs_y) * pix_per_mm)),
                      (int(((self.x + offs_x) + self.length) * pix_per_mm),
                       int(((self.y + offs_y) + self.length)  * pix_per_mm)), self.color, 1,)