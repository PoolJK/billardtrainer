import cv2

import numpy as np
from software.raspy.visual_items.table import MiniTable

pict_resolution_x = 1280
pict_resolution_y = 960
pict_pix_per_mm = 12.115

class Camera:
    """
    Taking pictures from camera and undistort them
    """

    def __init__(self):
        self.picture = []
        self.used_table = MiniTable()

    def take_picture(self):
        # take picture from camera
        capture = cv2.VideoCapture(0)
        if not capture.isOpened:
            print("Error access camera!")
            return -1

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, pict_resolution_x)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, pict_resolution_y)

        has_frame, self.picture = capture.read()
        if not has_frame:
            print("Error taking picture")
            return -1
        else:
            return self.picture


    def get_undistorted_image(self, image, table):
        """
        Get deskewed and resized image for beamer output
        :param table: detected table (rectangle for warp perspective)
        :return: corrected image image for output on beamer
        """

        print("found table: x: {}, y: {}, w:{}, h:{}, a:{}".format(table.x, table.y, table.w,
                                                                   table.h, table.angle))
        box1 = cv2.boxPoints(((table.x, table.y), (table.w, table.h), table.angle))
        print(box1)

        print("mini table: x: {}, y: {}, w:{}, h:{}, a:{}".format(self.used_table.x / pict_pix_per_mm,
                self.used_table.y / pict_pix_per_mm, self.used_table.w / pict_pix_per_mm,
                                        self.used_table.h / pict_pix_per_mm, self.used_table.angle))
        box2 = cv2.boxPoints(((self.used_table.x / pict_pix_per_mm, self.used_table.y / pict_pix_per_mm),
                              (self.used_table.w / pict_pix_per_mm, self.used_table.h / pict_pix_per_mm),
                                    self.used_table.angle))
        print(box2)

        pts_dst = np.array([box2[0], box2[1], box2[2], box2[3]])
        pts_src = np.array([box1[0], box1[1], box1[2], box1[3]])

        # Calculate the homography
        h, _ = cv2.findHomography(pts_src, pts_dst)

        # Warp source image to destination
        return cv2.warpPerspective(image, h, (image.shape[1], image.shape[0]))
