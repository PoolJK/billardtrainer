#!/usr/bin/python3

import cv2
import numpy as np


class Beamer:
    """
    A projector for showing image onto table.
    Needs to take offset and distance in account to correct displayed image.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height


    def getImage(self, table, image):
        """
        Get deskewed and resized image for beamer output
        :param table: detected table (rectangle for warp perspective)
        :return: corrected image image for output on beamer
        """
        # rotate table to positive 90 degrees area
        # if found_table.angle < -45.0:
        #     found_table.angle = (90.0 + found_table.angle)
        #     # otherwise, just take the inverse of the angle to make it positive
        # else:
        #     found_table.angle = -found_table.angle

        # rotate the image to deskew it
        # (h, w) = outPict.shape[:2]
        # center = (w // 2, h // 2)
        # M = cv2.getRotationMatrix2D(center, tableangle, 1.0)
        # rotated = cv2.warpAffine(outPict, M, (w, h), flags = cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        box = cv2.boxPoints(((table.x, table.y), (table.w, table.h), table.angle))
        # if args.debug:
        #     print("box: {}".format(box))

        table = np.copy(box)

        pts_dst = np.array([[1230, 910], [50, 910], [50, 50], [1230, 50]])
        pts_src = np.array([table[0], table[1], table[2], table[3]])

        # Calculate the homography
        h, _ = cv2.findHomography(pts_src, pts_dst)

        # Warp source image to destination
        im_dst = cv2.warpPerspective(image, h, (image.shape[1], image.shape[0]))
        return im_dst