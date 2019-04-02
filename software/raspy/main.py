#!/usr/bin/python3

import argparse
import sys
import cv2
import numpy as np
from ball import Ball
from table import Table, MiniTable

# set true if running tests on pc
ALGOTEST = True
# some defaults, put in beamer class later
IMAGEWIDTH = 1280
IMAGEHEIGHT = 960


def mouse_callback(event, x, y, flags, param):
    """
    print coordinates of mouse cursor on terminal
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


    if args.filename:
        """ Load image from disk if filename is given as parameter"""
        src = cv2.imread(args.filename, cv2.IMREAD_COLOR)
        # Check if image is loaded fine
        if src is None:
            print('Error opening image!')
            return -1

        cv2.imshow("Source Image", src)

        # create white image for output (height, width, dimension for numpy array)
        white = np.zeros((IMAGEHEIGHT, IMAGEWIDTH,  3), np.uint8)
        white[:] = (255, 255, 255)
        cv2.namedWindow("beamer")
        #cv2.setWindowProperty("beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback("beamer", mouse_callback)

    else:
        """ give out white image with beamer and take picture"""
        # create white image for beamer as light source
        white = np.zeros((IMAGEHEIGHT, IMAGEWIDTH, 3), np.uint8)
        white[:] = (255 ,255 ,255)
        cv2.namedWindow("beamer", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback("beamer", mouse_callback)
        # draw marker for beamer adjustment
        # cv2.circle(white, (50,50), 15, (35, 35, 205), 3)
        # cv2.circle(white, (1230,50), 15, (35, 35, 205), 3)
        # cv2.circle(white, (1230,910), 15, (35, 35, 205), 3)
        # cv2.circle(white, (50,910), 15, (35, 35, 205), 3)

        # show white image on beamer while taking picture
        cv2.imshow("beamer", white)
        cv2.waitKey()
        # time.sleep(5)

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


    # create black/white image to show found artefacts in
    outPict = np.zeros((IMAGEHEIGHT, IMAGEWIDTH ), np.uint8)

    # create gray image
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    if args.debug:
        cv2.imshow("gray", gray)

    #find table
    found_table = Table.find(gray)
    #draw table
    found_table.drawSelf(outPict)

    if args.debug:
        cv2.imshow("Found table", outPict)
        print("table: y: {}  y: {}  width: {}  height: {}  angle: {}"
              .format(found_table.x, found_table.y, found_table.width, found_table.height,found_table.angle))

    #find balls
    found_balls = Ball.find(gray)

    #draw balls (inside table)
    for ball in found_balls:
        #if(found_table.isInside(ball)):
        ball.draw(outPict)

    cv2.imshow("beamer", outPict)

    #    if (cv2.waitKey(30) & 0xFF) == 27:
    #       break

    cv2.waitKey()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    main()