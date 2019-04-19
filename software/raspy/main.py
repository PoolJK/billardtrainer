#!/usr/bin/python3

import argparse
import sys
import cv2
import numpy as np
from software.raspy.settings import Settings
from software.raspy.ball import Ball
from software.raspy.table import Table
from software.raspy.beamer import Beamer
from software.raspy.camera import Camera


# size of output window
IMAGEWIDTH = 1280
IMAGEHEIGHT = 960



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
    miniBeamer = Beamer(1280, 720)
    raspiCam = Camera()

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
        miniBeamer.show_image(white)
        cv2.waitKey()
        # time.sleep(5)
        src = raspiCam.take_picture(3280, 2464)
        if src is None:
            print('Error taking picture!')
            return -1


    if Settings.debugging:
        cv2.imshow("Source Image", src)

    #if args.debug:
    #   cv2.imshow("gray", gray)

    #find table
    found_table = Table.find(src)
    if found_table is not None:
        undistorted = raspiCam.get_undistorted_image(src, found_table)
    else:
        print("no table for correction found")
        return -1

    if Settings.debugging:
        cv2.imshow("undist", undistorted)

    #find table
    found_table = Table.find(undistorted)
    #draw table
    if found_table is not None:
        miniBeamer.add_object(found_table)
        print("table found")

    #find balls
    found_balls = Ball.find(undistorted)

    #draw balls (inside table)
    for ball in found_balls:
        #if(found_table.isInside(ball)):
        miniBeamer.add_object(ball)
        print("ball found")

    miniBeamer.show_objects()

    cv2.waitKey()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    main()