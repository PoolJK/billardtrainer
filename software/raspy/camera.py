import cv2
import numpy as np
import settings
from visual_items.table import MiniTable


class Camera:
    """
    Taking pictures from camera and undistort them
    """

    def __init__(self):
        self.picture = []
        self.ref_table = MiniTable()
        self.mount_height = settings.camera_mount_height
        self.pix_per_mm = settings.camera_pix_per_mm
        self.offset_x = settings.camera_offset_x
        self.offset_y = settings.camera_offset_y
        self.resolution_x = settings.camera_resolution_x
        self.resolution_y = settings.camera_resolution_y
        self.rotation = settings.camera_rotation


    def take_picture(self ):
        # take picture from camera
        capture = cv2.VideoCapture("http://192.168.178.23/live", cv2.CAP_FFMPEG)
        if not capture.isOpened:
            print("Error access camera!")
            return -1

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution_x)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution_y)

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

        #print("table found: x: {}, y: {}, w:{}, h:{}, a:{}".format(table.x, table.y, table.w, table.h, table.angle))

        box1 = cv2.boxPoints(((table.x, table.y), (table.w, table.h), table.angle))

        if settings.debugging:
            print("box1: {}".format(box1))
        #using mini table for undistortion, values already in mm
            print("mini table: x: {}, y: {}, w:{}, h:{}, a:{}".format(self.ref_table.x, self.ref_table.y,
                                                      self.ref_table.w, self.ref_table.h, self.ref_table.angle))
        box2 = cv2.boxPoints(((self.ref_table.x, self.ref_table.y),
                              (self.ref_table.w , self.ref_table.h), self.ref_table.angle))

        if settings.debugging:
            print("box2: {}".format(box2))

        pts_dst = np.array([box2[0], box2[1], box2[2], box2[3]])
        pts_src = np.array([box1[0], box1[1], box1[2], box1[3]])

        # Calculate the homography
        #h, _ = cv2.findHomography(pts_src, pts_dst)
        h = cv2.getPerspectiveTransform(pts_src, pts_dst)

        # Warp source image to destination
        warped_image = cv2.warpPerspective(image, h, (image.shape[1], image.shape[0]))
        if settings.debugging:
            # draw camera position
            # cv2.drawMarker(warped_image, (int(self.offset_x * self.pix_per_mm), int(self.offset_y * self.pix_per_mm)),
            #                (47, 255, 173), cv2.MARKER_CROSS, int(self.resolution_y), 2)
            print("camera position: x: {}, y: {} mm".format(int(self.offset_x * self.pix_per_mm),
                                                            int(self.offset_y * self.pix_per_mm)))
        return warped_image
