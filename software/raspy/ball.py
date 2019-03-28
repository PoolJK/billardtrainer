import cv2
import numpy as np


def static():
    pass


class Ball:
    """
    Holding information of a ball
    """
    def __init__(self,  position,  color):
        self.position = position
        self.color = [33, 55, 77]
    
    def draw(self):
        pass
    
    @static
    def testHoughParameters():
         panel = np.zeros([100, 700], np.uint8)
        cv2.namedWindow('panel')

        def nothing(x):
          pass

        cv2.createTrackbar('param1', 'panel', 1, 255, nothing)
        cv2.createTrackbar('param2', 'panel', 1, 255, nothing)
        cv2.createTrackbar('minRadius', 'panel', 1, 255, nothing)
        cv2.createTrackbar('maxRadius', 'panel', 1, 255, nothing)

        cv2.setTrackbarPos ('param1', 'panel', 50)
        cv2.setTrackbarPos ('param2', 'panel', 20)
        cv2.setTrackbarPos ('minRadius', 'panel', 1)
        cv2.setTrackbarPos ('maxRadius', 'panel', 30)
        while True:

        p1 = cv2.getTrackbarPos('param1', 'panel')
        if p1 < 1: p1 = 1
        p2 = cv2.getTrackbarPos('param2', 'panel')
        if p2 < 1: p2 = 1
        minR = cv2.getTrackbarPos('minRadius', 'panel')
        if minR < 1: minR = 1
        maxR = cv2.getTrackbarPos('maxRadius', 'panel')
        if maxR < 1: maxR = 1


    @static
    def find():
      """
        find balls
        """
        p1 = 50
        p2 = 29
        minR = 16
        maxR = 28
        rows = gray.shape[0]
        # print("{} {} {} {}".format(p1, p2, minR, maxR))

        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=p1, param2=p2, minRadius=minR,
                                   maxRadius=maxR)
        # circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=50, param2=20, minRadius=1, maxRadius=30)

        # cv2.rectangle(src, (150, 220), (1150, 800), (100, 100, 200), 3)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center = (i[0], i[1])
                # center = (i[0], i[1])
                # only circles inside table
                if (center[1] > 220):
                    print("Circle at: {}".format(center))
                    # circle center
                    cv2.circle(outPict, center, 1, (0, 100, 100), 3)
                    # circle outline
                    radius = i[2] + 10
                    cv2.circle(outPict, center, radius, (255, 0, 255), 3)
                    cv2.circle(src, center, radius, (255, 0, 255), 3)