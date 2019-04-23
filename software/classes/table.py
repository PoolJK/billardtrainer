#!/usr/bin/python3

import cv2
import numpy as np
from software.classes.ball import Ball


class Table:
    """
    All information needed for table
    """

    def __init__(self, x, y, width, height, angle, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.clothColor = color

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
        box = cv2.boxPoints(((self.x, self.y), (self.width, self.height), self.angle))
        # print("Rectangle at: {},{}, with size: {},{}, angle: {}".format(x, y, w, h, angle))
        box = np.int0(box)
        cv2.drawContours(outpict, [box], 0, (255, 0, 255), 2)
        # midpoint marker for testing
        cv2.circle(outpict, (self.x, self.y), 10, (255, 0, 255), 2)

    @staticmethod
    def find(grayimage):
        """ find table
            """
        _, thresh = cv2.threshold(grayimage, 100, 255, 0)
        # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        # binary = cv2.bitwise_not(gray)
        # cv2.imshow("thresh", thresh)
        # _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (x, y), (w, h), angle = cv2.minAreaRect(contour)
            if w > 300 and h > 200:
                # convert x, y w, h, angle to four points of rectangle
                # box = cv2.boxPoints(((x, y), (w * xStretch, h * yStretch), angle))
                # box = cv2.boxPoints(((x, y), (w, h), angle))
                # print("Rectangle at: {},{}, with size: {},{}, angle: {}".format(x, y, w, h, angle))
                # tableangle = angle
                # rotate table to 90 degrees
                # if tableangle < -45.0:
                #     tableangle = (90.0 + tableangle)
                #     # otherwise, just take the inverse of the angle to make it positive
                # else:
                #     tableangle = -tableangle
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
