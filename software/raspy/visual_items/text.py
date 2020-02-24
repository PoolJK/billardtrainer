from visual_items.visual_item import VisualItem
import cv2


class Text(VisualItem):
    def __init__(self, x, y, text):
        super().__init__(x,y, (255, 255, 255))
        self.text = text

    def draw_self(self, image, pix_per_mm, offs_x, offs_y) -> None:
        cv2.putText(image, self.text, (int((self.x - offs_x) * pix_per_mm + (image.shape[1] / 2)),
                                       int((self.y - offs_y) * pix_per_mm + (image.shape[0] / 2))),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.color, 1)


