#!/usr/bin/python3
import cv2
import numpy as np


class Ball:
    """
    Holding information of a ball
    """

    # HoughCircles parameters
    p1 = 50
    p2 = 29
    minR = 16
    maxR = 28

    def __init__(self,  position, radius,  color=[33, 55, 77]):
        self.position = position
        self.radius = radius
        self.color = color

    
    def draw(self, outpict):
        #circle center
        cv2.circle(outpict, self.position, 1, (0, 100, 100), 3)
        # circle outline
        cv2.circle(outpict, self.position, self.radius + 10, (255, 0, 255), 3)


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
    def find(grayimage):
        """
        find balls in image
        """
        rows = grayimage.shape[0]
        # print("{} {} {} {}".format(p1, p2, minR, maxR))

        # find circles in image
        circles = cv2.HoughCircles(grayimage, cv2.HOUGH_GRADIENT, 1, rows / 8, param1 = Ball.p1,
                                   param2 = Ball.p2, minRadius = Ball.minR, maxRadius = Ball.maxR)

        balls = []

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center = (i[0], i[1])
                balls.append(Ball(center, i[2]))

        return balls
