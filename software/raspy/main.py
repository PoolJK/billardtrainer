#!/usr/bin/python3

import argparse
import sys
import threading
from time import sleep
from queue import Queue
import cv2
import numpy as np
import settings
from ball import Ball
from table import Table
from beamer import Beamer
from web import webserv


class Photo(Exception):
    def __init__(self, msg):
        print(msg)
        #cv2.destroyAllWindows()
        sys.exit(-1)


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
    print("OpenCV version :  {0}".format(cv2.__version__))
    clParser = argparse.ArgumentParser()
    clParser.add_argument('-p', '--platform', dest="platform", help="Platform to run on ('pi' for Raspi, 'win' for Windows)",
                          required=True)
    clParser.add_argument('-f', '--file', dest="filename", help="image file to process",
                          required=False)
    clParser.add_argument('-d', '--debug',  dest="debug", help="show more debug output",
                          action="store_true", default=False)

    args = clParser.parse_args()

    if args.debug:
        settings.debugging = True
    else:
        settings.debugging = False

    if args.platform == 'pi':
        settings.on_raspy = True
    else:
        settings.on_raspy = False

    if args.platform == 'win':
        settings.on_win = True
    else:
        settings.on_win = False

    webq = Queue()

    #start Flask webserver in background
    webserv.websetup(webq)
    webThread = threading.Thread(target=webserv.wapp.run, daemon=True).start()

    # create window for result output (height, width, dimension for numpy array)
    if settings.on_raspy:
        cv2.namedWindow("result", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("result", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
        cv2.namedWindow("result")

    # get image from file or camera
    if args.filename:
        """ Load image from disk if filename is given as parameter"""
        src = cv2.imread(args.filename, cv2.IMREAD_COLOR)
        # Check if image is loaded fine
        if src is None:
            raise Photo('Error opening image!')
        cv2.imshow("Source Image", src)
    else:
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
        
        # take picture from camera
        capture = cv2.VideoCapture(0)
        if not capture.isOpened:
            raise Photo("Error access camera!")

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGEWIDTH)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGEHEIGHT)

        has_frame, src = capture.read()
        if not has_frame:
            raise Photo("Error taking picture")

    # attach mouse callback to window for measuring
    cv2.setMouseCallback("result", mouse_callback)


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

    # if settings.debugging:
    #     cv2.imshow("Found table", outPict)
    #     print("table: y: {}  y: {}  width: {}  height: {}  angle: {}"
    #           .format(found_table.x, found_table.y, found_table.w, found_table.h, found_table.angle))

    while webq.get() == 'Start':
        #clear result image
        outPict[:] = (0, 0, 0)

        # draw table
        if found_table is not None:
            found_table.drawSelf(outPict)

        #find balls
        found_balls = Ball.find(gray)

        #draw balls (inside table)
        for ball in found_balls:
            #if(found_table.isInside(ball)):
            ball.draw(outPict)

        if settings.on_raspy:
            cv2.imshow("./web/static/result", miniBeamer.getImage(found_table, outPict))
        else:
            cv2.imshow("result", outPict)

        cv2.imwrite("./web/static/result.jpg", outPict)
        cv2.waitKey(1)
        #    if (cv2.waitKey(30) & 0xFF) == 27:
        #       break
        #cv2.waitKey()

    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    main()