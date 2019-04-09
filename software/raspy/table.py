#!/usr/bin/python3

import cv2
import numpy as np
import settings
from ball import Ball


class Table:
    """
    Parameters and functions for Tables
    """
    def __init__(self, x, y,  width, height, angle, color=[30, 25, 10]):
        """
        Create new table object
        :param x: x-position of center in pixels
        :param y: y-position of center in pixels
        :param width: width in pixels
        :param height: height in pixels
        :param angle: angle in degrees
        :param color: color of cloth
        """
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.angle = angle
        self.clothColor = color


    def isInside(self, ball: Ball) -> bool:
        """
        Check if ball is inside table
        """
        if(ball.x > self.x and ball.x < self.x + self.w and
            ball.y > self.y and ball.y < self.y + self.h):
            return True
        else:
            return False


    def drawSelf(self, outpict):
        """
        Draw tabel rectangle
        :param outpict: image to draw on
        """
        box = cv2.boxPoints(((self.x, self.y), (self.w, self.h), self.angle))
        #print("Rectangle at: {},{}, with size: {},{}, angle: {}".format(x, y, w, h, angle))
        box = np.int0(box)
        cv2.drawContours(outpict, [box],  0, (255, 255, 255), 2)
        # midpoint marker for testing
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
        # _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if settings.on_raspy:
            _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (x, y), (w, h), angle = cv2.minAreaRect(contour)
            if w > 300 and h > 200:
                # convert x, y w, h, angle to four points of rectangle
                # box = cv2.boxPoints(((x, y), (w * xStretch, h * yStretch), angle))
                box = cv2.boxPoints(((x, y), (w, h), angle))
                print("Box: {}".format(box))
                # convert to integer
                #box = np.int0(box)
                return Table(x, y, w, h, angle)




class SnookerTable(Table):
    """
    Snooker table default values
    """
    def __init__(self):
        super().__init__(0, 0, 3556, 1778, [34, 55, 88])


class MiniTable(Table):
    """
    Mini table used for testing purposes
    """
    def __init__(self):
        super().__init__(0, 0, 840, 440, [34, 55, 88])


