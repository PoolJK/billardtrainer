import cv2
import numpy as np
from software.raspy.visual_items.visual_item import VisualItem
from software.raspy.settings import Settings


class Ball(VisualItem):
    """
    Parameters and functions for a billiard ball
    """

    # HoughCircles parameters
    p1 = 50
    p2 = 29
    minR = 16
    maxR = 28

    def __init__(self, x, y, radius,  color=[33, 55, 77]):
        """
        Generate new ball
        :param x: x-position of center in mm
        :param y: y-position of center in mm
        :param radius: radius in mm
        :param color: ball color
        """
        super().__init__(x, y, color)
        self.radius = radius

    
    def draw_self(self, image, pix_per_mm, offs_x, offs_y) -> None:
        if Settings.debugging:
            print("ball drawn at: x:{}, y:{} (pixels)".format( int((self.x - offs_x) * pix_per_mm + (image.shape[1] / 2)),
                                                    int((self.y - offs_y) * pix_per_mm + (image.shape[0] / 2))))
        # circle outline
        cv2.circle(image, (int((self.x - offs_x) * pix_per_mm + (image.shape[1] / 2)),
                           int((self.y - offs_y) * pix_per_mm + (image.shape[0] / 2))),
                            int(self.radius * pix_per_mm), (255, 255, 255), 3)
        # draw mid point for debugging
        if Settings.debugging:
            cv2.drawMarker(image, (int((self.x - offs_x) * pix_per_mm + (image.shape[1] / 2)),
                                   int((self.y - offs_y) * pix_per_mm + (image.shape[0] / 2))),
                                 (0, 0, 255), cv2.MARKER_CROSS, 10, 1)

    @staticmethod
    def find_self(image, pix_per_mm, offs_x, offs_y):
        """
        Find balls in image
        :param grayimage: Image for houghCircles algorithm
        :return: list with found balls
        """
        # create gray image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        rows = gray.shape[0]
        # print("{} {} {} {}".format(p1, p2, minR, maxR))

        # find circles in image
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=Ball.p1,
                                   param2=Ball.p2, minRadius=Ball.minR, maxRadius=Ball.maxR)
        # found circles with position in pixels relative from image origin in upper left corner
        balls = []
        if circles is not None:
            for i in circles[0, :]:
                # get relative position from image origin, convert to mm and subtract camera offset
                balls.append(Ball(((i[0] - (image.shape[1] / 2)) / pix_per_mm) - offs_x,
                                   ((i[1] - (image.shape[0] / 2)) / pix_per_mm) - offs_y,
                                   i[2] / pix_per_mm))
                if Settings.debugging:
                    print("ball found: x:{}, y:{} (mm)".format(((i[0] - (image.shape[1] / 2))/ pix_per_mm) - offs_x,
                                                           ((i[1] - (image.shape[0] / 2))/ pix_per_mm) - offs_y))
        return balls
