import cv2
import numpy as np

class Table:
    """
    All information needed for table
    """
    def find(self):
        """ find table
            """
        _, thresh = cv2.threshold(gray, 100, 255, 0)
        # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        # binary = cv2.bitwise_not(gray)
        # cv2.imshow("thresh", thresh)
        # _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (x, y), (w, h), angle = cv2.minAreaRect(contour)
            if w > 300 and h > 200:
                # convert x, y w, h, angle to four points of rectangle
                # box = cv2.boxPoints(((x, y), (w * xStretch, h * yStretch), angle))
                box = cv2.boxPoints(((x, y), (w, h), angle))
                print("Rectangle at: {},{}, with size: {},{}, angle: {}".format(x, y, w, h, angle))
                tableangle = angle
                # convert to integer
                box = np.int0(box)
                table = np.copy(box)
                # print(table)
                # print(box)
                cv2.drawContours(outPict, [box], 0, (255, 0, 255), 2)
                cv2.drawContours(src, [box], 0, (255, 0, 255), 2)

        # rotate table to 90 degrees
        if tableangle < -45.0:
            tableangle = (90.0 + tableangle)
            # otherwise, just take the inverse of the angle to make it positive
        else:
            tableangle = -tableangle



class SnookerTable(Table):
    """
    Snooker table default values
    """
    def __init__(self):
        self.size = np.array([3556, 1778])
        self.clothColor = [34, 55, 88]
