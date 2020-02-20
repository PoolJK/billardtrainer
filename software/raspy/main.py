#!/usr/bin/python3

import argparse
import cv2
import numpy as np
from software.raspy.settings import Settings
from software.raspy.visual_items.ball import Ball
from software.raspy.visual_items.table import Table, MiniTable
from software.raspy.visual_items.cross import Cross
from software.raspy.beamer import Beamer
from software.raspy.camera import Camera


def main():
    #print("OpenCV version :  {0}".format(cv2.__version__))
    clParser = argparse.ArgumentParser()
    clParser.add_argument('-f', '--file', dest="filename", help="image file to process",
                          required=False)
    clParser.add_argument('-d', '--debug',  dest="debug", help="show more debug output",
                          action="store_true", default=False)

    args = clParser.parse_args()

    if args.debug:
        Settings.debugging = True
    else:
        Settings.debugging = False

    if args.filename:
        Settings.on_raspy = False
    else:
        Settings.on_raspy = True

    # create Beamer and Camera for taking picture and showing results
    miniBeamer = Beamer()
    raspiCam = Camera()
    minTable = MiniTable()

    # get image from file or camera
    if args.filename:
        """ Load image from disk if filename is given as parameter"""
        src = cv2.imread(args.filename, cv2.IMREAD_COLOR)
        # Check if image is loaded fine
        if src is None:
            print('Error opening image!')
            return -1
    else:
        """ give out white image with beamer and take picture"""
        miniBeamer.show_white()
        cv2.waitKey()
        # time.sleep(5)
        src = raspiCam.take_picture(1280, 720)
        if src is None:
            print('Error taking picture!')
            return -1

    if Settings.debugging:
        cv2.namedWindow("source", cv2.WINDOW_NORMAL)
        cv2.imshow("source", src)

    #if args.debug:
    #   cv2.imshow("gray", gray)

    #find table of undistortion
    found_table = Table.find_self(src, raspiCam.pix_per_mm, raspiCam.offset_x, raspiCam.offset_y)

##    if found_table is not None:
##        # get undistorted image
##        undistorted = raspiCam.get_undistorted_image(src, found_table)
##        if Settings.debugging:
##            #draw found table and reference table in source image after recognition
##            found_table.draw_self(src, raspiCam.pix_per_mm, raspiCam.offset_x, raspiCam.offset_y)
##            minTable.draw_self(src, raspiCam.pix_per_mm,raspiCam.offset_x, raspiCam.offset_y)
##            cv2.imshow("source", src)
##    else:
##        print("no table for correction found")
##        return -1

    #find table in undistorted image
##    found_table = Table.find_self(undistorted, raspiCam.pix_per_mm, raspiCam.offset_x, raspiCam.offset_y)

    if found_table is not None:
        miniBeamer.add_object(found_table)
        #if Settings.debugging:
        #     found_table.draw_self(undistorted, raspiCam.pix_per_mm, 0, 0)
        #    print("undistorted table: x: {}, y: {}, w: {}, h: {}".format(found_table.x, found_table.y,
        #                                                            found_table.w,found_table.h))
    else:
        print("No table in undistorted found!")

##    if Settings.debugging:
##        cv2.namedWindow("undist", cv2.WINDOW_NORMAL)
##        cv2.imshow("undist", undistorted)

    #find balls
    found_balls = Ball.find_self(src, raspiCam.pix_per_mm, raspiCam.offset_x, raspiCam.offset_y)

    #draw balls (inside table)
    for ball in found_balls:
        #if(found_table.isInside(ball)):
        miniBeamer.add_object(ball)
        #print("ball found")
    miniBeamer.show_objects()

    if Settings.debugging:
        # draw found table in undistorted image
##        if found_table is not None:
##            found_table.draw_self(undistorted, raspiCam.pix_per_mm, raspiCam.offset_x, raspiCam.offset_y)
        # draw mid point cross hair in images
        cv2.drawMarker(src, (int(src.shape[1] / 2), int(src.shape[0] / 2)),
                       (0, 165, 255), cv2.MARKER_CROSS, int(src.shape[1]), 2)
        cv2.imshow("source", src)

##        cv2.drawMarker(undistorted, (int(undistorted.shape[1] / 2), int(undistorted.shape[0] / 2)),
##                       (0, 165, 255), cv2.MARKER_CROSS, int(undistorted.shape[1]), 2)
##        cv2.imshow("undist", undistorted)

    cv2.waitKey()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    main()