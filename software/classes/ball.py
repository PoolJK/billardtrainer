#!/usr/bin/python3
import cv2
import numpy as np
import raspy.settings as settings


class Ball:
    """
    Parameters and functions for ball
    """

    # HoughCircles parameters
    gradient_value = 50
    accumulator_threshold = 29
    min_radius = 16
    max_radius = 28

    def __init__(self, x, y, radius, color=None):
        """
        Generate new ball
        :param x: x-position of center in pixles
        :param y: y-position of center in pixels
        :param radius: radius in pixels
        :param color: ball color
        """
        if color is None:
            color = [33, 55, 77]
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, outpict):
        # draw mid point for debugging
        if settings.debugging:
            cv2.drawMarker(outpict, (int(self.x), int(self.y)), (255, 255, 255), cv2.MARKER_CROSS, 20, 10)
        # circle outline
        cv2.circle(outpict, (int(self.x), int(self.y)), int(self.radius) + 10, (255, 255, 255), 10)

    # @staticmethod
    # def nothing(x):
    #     pass

    # @staticmethod
    # def testParametersOnline():
    #     """
    #     test detecting algo with online values
    #     """
    #     panel = np.zeros([100, 700], np.uint8)
    #     cv2.namedWindow('panel')
    #
    #     cv2.createTrackbar('param1', 'panel', 1, 255, nothing)
    #     cv2.createTrackbar('param2', 'panel', 1, 255, nothing)
    #     cv2.createTrackbar('minRadius', 'panel', 1, 255, nothing)
    #     cv2.createTrackbar('maxRadius', 'panel', 1, 255, nothing)
    #
    #     cv2.setTrackbarPos ('param1', 'panel', 50)
    #     cv2.setTrackbarPos ('param2', 'panel', 20)
    #     cv2.setTrackbarPos ('minRadius', 'panel', 1)
    #     cv2.setTrackbarPos ('maxRadius', 'panel', 30)
    #
    #     while True:
    #         p1 = cv2.getTrackbarPos('param1', 'panel')
    #         if p1 < 1: p1 = 1
    #         p2 = cv2.getTrackbarPos('param2', 'panel')
    #         if p2 < 1: p2 = 1
    #         minR = cv2.getTrackbarPos('minRadius', 'panel')
    #         if minR < 1: minR = 1
    #         maxR = cv2.getTrackbarPos('maxRadius', 'panel')
    #         if maxR < 1: maxR = 1
    #         Ball.find()

    @staticmethod
    def find(img, dp=1, min_dist=1, gradient_value=None, accumulator_threshold=None, min_radius=None, max_radius=None):
        if gradient_value is None:
            gradient_value = Ball.gradient_value
        if accumulator_threshold is None:
            accumulator_threshold = Ball.accumulator_threshold
        if min_radius is None:
            min_radius = Ball.min_radius
        if max_radius is None:
            max_radius = Ball.max_radius
        # print("{} {} {} {} {} {}".format(dp, min_dist, gradient_value, accumulator_threshold, min_radius, max_radius))

        # find circles in image
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=dp, minDist=min_dist, param1=gradient_value,
                                   param2=accumulator_threshold, minRadius=min_radius, maxRadius=max_radius)

        balls = []

        if circles is not None:
            for i in circles[0, :]:
                balls.append(Ball(i[0], i[1], i[2]))

        return balls
