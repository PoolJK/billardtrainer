import cv2
import numpy as np
from software.raspy.settings import Settings
from software.raspy.camera import pict_pix_per_mm


class Ball:
    """
    Parameters and functions for ball
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
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    
    def draw_self(self, outpict):
        # draw mid point for debugging
        if Settings.debugging:
            cv2.drawMarker(outpict, (int(self.x), int(self.y)), (0, 0, 255), cv2.MARKER_CROSS, 10, 1)
        # circle outline
        cv2.circle(outpict, (int(self.x), int(self.y)), int(self.radius) + 5, (255, 255, 255), 3)


    @staticmethod
    def find(image):
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
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1 = Ball.p1,
                                   param2 = Ball.p2, minRadius = Ball.minR, maxRadius = Ball.maxR)

        balls = []

        if circles is not None:
            for i in circles[0, :]:
                balls.append(Ball(i[0] / pict_pix_per_mm, i[1] / pict_pix_per_mm, i[2] / pict_pix_per_mm))

        return balls
