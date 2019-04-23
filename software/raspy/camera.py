import cv2
import numpy as np
from software.raspy.visual_items.table import MiniTable


class Camera:
    """
    Taking pictures from camera and undistort them
    """

    def __init__(self, res_x=1280, res_y=960, ppm=12.115):
        self.pict_resolution_x = res_x
        self.pict_resolution_y = res_y
        self.pict_pix_per_mm = ppm
        self.picture = []
        self.used_table = MiniTable()

    def take_picture(self):
        # take picture from camera
        capture = cv2.VideoCapture(0)
        if not capture.isOpened:
            print("Error access camera!")
            return -1

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.pict_resolution_x)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.pict_resolution_y)

        has_frame, self.picture = capture.read()
        if not has_frame:
            print("Error taking picture")
            return -1
        else:
            return self.picture

    def get_undistorted_image(self, image, table):
        """
        Get deskewed and resized image for beamer output
        :param image: the image to undistort
        :param table: detected table (rectangle for warp perspective)
        :return: corrected image image for output on beamer
        """

        print("found table: x: {}, y: {}, w:{}, h:{}, a:{}".format(table.x, table.y, table.w,
                                                                   table.h, table.angle))
        box1 = cv2.boxPoints(((table.x, table.y), (table.w, table.h), table.angle))
        print(box1)

        print("mini table: x: {}, y: {}, w:{}, h:{}, a:{}".format(self.used_table.x / self.pict_pix_per_mm,
                                                                  self.used_table.y / self.pict_pix_per_mm,
                                                                  self.used_table.w / self.pict_pix_per_mm,
                                                                  self.used_table.h / self.pict_pix_per_mm,
                                                                  self.used_table.angle))
        box2 = cv2.boxPoints(((self.used_table.x / self.pict_pix_per_mm, self.used_table.y / self.pict_pix_per_mm),
                             (self.used_table.w / self.pict_pix_per_mm, self.used_table.h / self.pict_pix_per_mm),
                             self.used_table.angle))
        print(box2)

        pts_dst = np.array([box2[0], box2[1], box2[2], box2[3]])
        pts_src = np.array([box1[0], box1[1], box1[2], box1[3]])

        # Calculate the homography
        h, _ = cv2.findHomography(pts_src, pts_dst)

        # Warp source image to destination
        return cv2.warpPerspective(image, h, (image.shape[1], image.shape[0]))
