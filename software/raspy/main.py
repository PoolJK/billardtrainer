#!/usr/bin/python3

import argparse
import cv2
import numpy as np
from software.raspy.settings import Settings
from software.raspy.visual_items.ball import Ball
from software.raspy.visual_items.table import Table
from software.raspy.beamer import Beamer
from software.raspy.camera import Camera


# size of output window
IMAGEWIDTH = 1280
IMAGEHEIGHT = 960


def main():
    # print("OpenCV version :  {0}".format(cv2.__version__))
    cl_parser = argparse.ArgumentParser()
    cl_parser.add_argument('-f', '--file', dest="filename", help="image file to process",
                           required=False)
    cl_parser.add_argument('-d', '--debug',  dest="debug", help="show more debug output",
                           action="store_true", default=False)

    args = cl_parser.parse_args()

    if args.debug:
        Settings.debugging = True
    else:
        Settings.debugging = False

    if args.filename:
        Settings.on_raspy = False
    else:
        Settings.on_raspy = True

    # create Beamer and Camera for taking picture and showing results
    mini_beamer = Beamer()
    raspi_cam = Camera()

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
        # create white image for beamer as light source
        white = np.zeros((IMAGEHEIGHT, IMAGEWIDTH, 3), np.uint8)
        white[:] = (255, 255, 255)
        mini_beamer.show_image(white)
        cv2.waitKey()
        # time.sleep(5)
        src = raspi_cam.take_picture()
        if src is None:
            print('Error taking picture!')
            return -1

    if Settings.debugging:
        cv2.imshow("Source Image", src)

    # if args.debug:
    #   cv2.imshow("gray", gray)

    # find table
    found_table = Table.find_self(src)
    if found_table is not None:
        undistorted = raspi_cam.get_undistorted_image(src, found_table)
    else:
        print("no table for correction found")
        return -1

    # find table
    found_table = Table.find_self(undistorted)
    # draw table
    # found_table = MiniTable()
    if found_table is not None:
        mini_beamer.add_visual_item(found_table)
        if Settings.debugging:
            found_table.draw_self(undistorted)

        if Settings.debugging:
            cv2.imshow("undist", undistorted)

        # find balls
        found_balls = Ball.find_self(undistorted, raspi_cam.pict_pix_per_mm)

        # draw balls (inside table)
        for ball in found_balls:
            # if(found_table.isInside(ball)):
            mini_beamer.add_visual_item(ball)
            # print("ball found")

        mini_beamer.show_visual_items()

    cv2.waitKey()
    cv2.destroyAllWindows()
    return 0


main()
