#!/usr/bin/python3

import cv2
import numpy as np
import settings
from ball import Ball


class Table:
    """
    Parameters and functions for Tables
    """
    x = y = width = height = angle = cloth_color = None

    def __init__(self, x, y, width, height, angle, cloth_color=None):
        """
        Create new table object
        :param x: x-position of center in pixels
        :param y: y-position of center in pixels
        :param width: width in pixels
        :param height: height in pixels
        :param angle: angle in degrees
        :param cloth_color: color of cloth
        """
        if cloth_color is None:
            cloth_color = [30, 25, 10]
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.cloth_color = cloth_color

    def is_inside(self, ball: Ball) -> bool:
        """
        Check if ball is inside table
        """
        if (self.x < ball.x < self.x + self.width and
                self.y < ball.y < self.y + self.height):
            return True
        else:
            return False

    def draw_self(self, outpict):
        """
        Draw table rectangle
        :param outpict: image to draw on
        """
        box = cv2.boxPoints(((self.x, self.y), (self.width, self.height), self.angle))
        # print("Rectangle at: {},{}, with size: {},{}, angle: {}".format(x, y, w, h, angle))
        box = np.int0(box)
        cv2.drawContours(outpict, [box], 0, (255, 0, 255), 2)
        # midpoint marker for testing
        cv2.circle(outpict, (self.x, self.y), 10, (255, 0, 255), 2)
        if settings.debugging:
            cv2.drawMarker(outpict, (int(self.x), int(self.y)), (0, 0, 255), cv2.MARKER_CROSS, 15, 1)

    @staticmethod
    def find(grayimage):
        """
        Find table rectangle in image
        :param grayimage: Gray image for findContours algorithm
        :return: new Table object
        """
        _, thresh = cv2.threshold(grayimage, 100, 255, 0)
        # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        # binary = cv2.bitwise_not(gray)
        # cv2.imshow("thresh", thresh)
        if '{}.{}'.format(cv2.getVersionMajor(), cv2.getVersionMinor()) == '3.4':
            _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (x, y), (w, h), angle = cv2.minAreaRect(contour)
            if w > 300 and h > 200:
                # convert x, y w, h, angle to four points of rectangle
                box = cv2.boxPoints(((x, y), (w, h), angle))
                print("Box: {}".format(box))
                # convert to integer
                # box = np.int0(box)
                return Table(int(x), int(y), int(w), int(h), int(angle), [30, 25, 10])


class SnookerTable(Table):
    """
    Snooker table default values
    """

    def __init__(self):
        super().__init__(0, 0, 3556, 1778, 0, [34, 55, 88])


class MiniTable(Table):
    """
    Mini table used for testing purposes
    """

    def __init__(self):
        super().__init__(0, 0, 840, 440, 0, [34, 55, 88])
