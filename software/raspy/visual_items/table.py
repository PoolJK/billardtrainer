import cv2
import numpy as np
from software.raspy.settings import Settings
from software.raspy.visual_items.visual_item import VisualItem
#from software.raspy.ball import Ball


class Table(VisualItem):
    """
    Parameters and functions for a billiard tables
    """
    def __init__(self, x, y,  width, height, angle, color=[30, 25, 10]):
        """
        Create new table object
        :param x: x-position of center in mm
        :param y: y-position of center in mm
        :param width: width in mm
        :param height: height in mm
        :param angle: angle in degrees
        :param color: color of cloth
        """
        super().__init__(x, y, color)
        self.w = width
        self.h = height
        self.angle = angle


    # def is_inside(self, ball: Ball) -> bool:
    #     """
    #     Check if ball is inside table
    #     """
    #     if(ball.x > self.x and ball.x < self.x + self.w and
    #         ball.y > self.y and ball.y < self.y + self.h):
    #         return True
    #     else:
    #         return False


    def draw_self(self, image, pix_per_mm, offs_x, offs_y) -> None:
        box = cv2.boxPoints((((self.x - offs_x) * pix_per_mm + (image.shape[1] / 2),
                              (self.y - offs_y) * pix_per_mm + (image.shape[0] / 2)),
                              (self.w * pix_per_mm, self.h * pix_per_mm), self.angle))
        # if Settings.debugging:
        #     print("Rectangle at: {},{}, with size: {},{}, angle: {}".format(self.x, self.y, self.w, self.h, self.angle))
        box = np.int0(box)
        cv2.drawContours(image, [box],  0, (255, 255, 255), 2)
        # draw mid point for debugging
        if Settings.debugging:
            print("table drawn: x: {}, y: {}, w: {}, h: {}, a: {} (pixels)"
                  .format((self.x - offs_x) * pix_per_mm + (image.shape[1] / 2),
                          (self.y - offs_y) * pix_per_mm + (image.shape[0] / 2),
                           self.w * pix_per_mm, self.h * pix_per_mm, self.angle))

            cv2.drawMarker(image, (int((self.x - offs_x) * pix_per_mm + (image.shape[1] / 2)),
                                   int((self.y - offs_y) * pix_per_mm + (image.shape[0] / 2))),
                                    (0, 0, 255), cv2.MARKER_CROSS, 10, 1)


    @staticmethod
    def find_self(image, pix_per_mm, offs_x, offs_y):
        # create gray image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        _, thresh = cv2.threshold(gray, 100, 255, 0)
        # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        # binary = cv2.bitwise_not(gray)
        # cv2.imshow("thresh", thresh)
        # _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if Settings.on_raspy:
            _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (x, y), (w, h), angle = cv2.minAreaRect(contour)
            if w > 300 and h > 200:
                if Settings.debugging:
                    print("table found: x: {}, y:{}, w: {}, h: {}, a:{} (mm)"
                          .format(((x - (image.shape[1] / 2)) / pix_per_mm) - offs_x,
                                  ((y - (image.shape[0] / 2)) / pix_per_mm) - offs_y,
                                    w / pix_per_mm, h / pix_per_mm, angle))
        # get relative position from image origin, convert to mm and subtract camera offset
                return Table(((x - (image.shape[1] / 2)) / pix_per_mm) - offs_x,
                             ((y - (image.shape[0] / 2)) / pix_per_mm) - offs_y,
                               w / pix_per_mm, h / pix_per_mm, angle)


class SnookerTable(Table):
    """
    Snooker table default values
    """
    def __init__(self):
        super().__init__(0, 0, 3556, 1778, 0, [34, 55, 88])


class MiniTable(Table):
    """
    Mini table used for testing purposes
    Measured at the boarder between cushions and wooden frame
    """
    def __init__(self):
        super().__init__(0, 0, 480, 880, -90.0, [34, 55, 88])


