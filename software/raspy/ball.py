#!/usr/bin/python3
import cv2
import settings


class Ball:
    """
    Parameters and functions for ball
    """

    # HoughCircles parameters
    p1 = 50
    p2 = 29
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
            cv2.drawMarker(outpict, (int(self.x), int(self.y)), (0, 0, 255), cv2.MARKER_CROSS, 10, 1)
        # circle outline
        cv2.circle(outpict, (int(self.x), int(self.y)), int(self.radius) + 5, (255, 255, 255), 3)

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
        Find balls in image
        :param grayimage: gray image for houghCircles algorithm
        :return: list with found balls
        """
        rows = grayimage.shape[0]
        # print("{} {} {} {}".format(p1, p2, minR, maxR))

        # find circles in image
        circles = cv2.HoughCircles(grayimage, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=Ball.p1,
                                   param2=Ball.p2, minRadius=Ball.min_radius, maxRadius=Ball.max_radius)

        balls = []

        if circles is not None:
            for i in circles[0, :]:
                balls.append(Ball(i[0], i[1], i[2]))

        return balls
