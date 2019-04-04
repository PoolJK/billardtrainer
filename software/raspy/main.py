#!/usr/bin/python3

import argparse
import sys
import cv2
import numpy as np
import settings
from ball import Ball
from table import Table
from beamer import Beamer


# size of output window
IMAGEWIDTH = 1280
IMAGEHEIGHT = 960


def mouse_callback(event, x, y, flags, param):
    """
    print coordinates of mouse on click
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Coord: {} {}".format(x, y))


def main():
    clParser = argparse.ArgumentParser()
    clParser.add_argument('-f', '--file', dest="filename", help="image file to process",
                          required=False)
    clParser.add_argument('-d', '--debug',  dest="debug", help="show more debug output",
                          action="store_true", default=False)

    args = clParser.parse_args()

    if args.debug:
        settings.debugging = True

    if args.filename:
        settings.on_raspy = False


    # get image from file or camera
    if args.filename:
        """ Load image from disk if filename is given as parameter"""
        src = cv2.imread(args.filename, cv2.IMREAD_COLOR)
        # Check if image is loaded fine
        if src is None:
            print('Error opening image!')
            return -1

        cv2.imshow("Source Image", src)
    else:
        # take picture from camera
        capture = cv2.VideoCapture(0)
        if not capture.isOpened:
            print("Error access camera!")
            return -1

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGEWIDTH)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGEHEIGHT)

        has_frame, src = capture.read()
        if not has_frame:
            print("Error taking picture")
            return -1

    # create window for result output (height, width, dimension for numpy array)
    if settings.on_raspy:
        cv2.namedWindow("result", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("result", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
        cv2.namedWindow("result")

    cv2.setMouseCallback("result", mouse_callback)

    if settings.on_raspy:
        miniBeamer = Beamer(1280, 720)
        """ give out white image with beamer and take picture"""
        # create white image for beamer as light source
        white = np.zeros((IMAGEHEIGHT, IMAGEWIDTH, 3), np.uint8)
        white[:] = (255, 255, 255)
        # cv2.circle(white, (50,50), 15, (35, 35, 205), 3)
        # cv2.circle(white, (1230,50), 15, (35, 35, 205), 3)
        # cv2.circle(white, (1230,910), 15, (35, 35, 205), 3)
        # cv2.circle(white, (50,910), 15, (35, 35, 205), 3)

        # show white image on beamer while taking picture
        cv2.imshow("result", white)
        cv2.waitKey()
        # time.sleep(5)

    # create black image to show found artefacts in
    outPict = np.zeros((IMAGEHEIGHT, IMAGEWIDTH, 3 ), np.uint8)
    outPict[:] = (0, 0, 0)

    # create gray image
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    #if args.debug:
    #   cv2.imshow("gray", gray)

    #find table
    found_table = Table.find(gray)
    #draw table
    if found_table is not None:
        found_table.drawSelf(outPict)

    if settings.debugging:
        cv2.imshow("Found table", outPict)
        print("table: y: {}  y: {}  width: {}  height: {}  angle: {}"
              .format(found_table.x, found_table.y, found_table.w, found_table.h, found_table.angle))

    #find balls
    found_balls = Ball.find(gray)

    #draw balls (inside table)
    for ball in found_balls:
        #if(found_table.isInside(ball)):
        ball.draw(outPict)

    if settings.on_raspy:
        cv2.imshow("result", miniBeamer.getImage(found_table, outPict))
    else:
        cv2.imshow("result", outPict)

    #    if (cv2.waitKey(30) & 0xFF) == 27:
    #       break

    cv2.waitKey()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    main()