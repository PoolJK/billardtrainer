from software.raspy.visual_items.visual_item import VisualItem
import cv2


class Text(VisualItem):
    def __init__(self, x, y, text):
        super().__init__(x,y, (255, 255, 255))
        self.text = text

    def draw_self(self, image) -> None:
        cv2.putText(image, self.text, (int(self.x), int(self.y)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, self.color, 1)


