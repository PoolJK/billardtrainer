#!/usr/bin/python3

import argparse
import sys
import cv2
import threading
from queue import Queue
import numpy as np
import settings
from visual_items.ball import Ball
from visual_items.table import Table, MiniTable
from visual_items.cross import Cross
from beamer import Beamer
from camera import Camera
from web.webserv import Webserver


class GetImage(Exception):
    def __init__(self, msg):
        print(msg)
        # cv2.destroyAllWindows()
        sys.exit(-1)


def mouse_callback(event, x, y, flags, param):
    """
    print coordinates of mouse on click
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Coord: {} {}".format(x, y))


def main():
    print("OpenCV version :  {0}".format(cv2.__version__))
    clParser = argparse.ArgumentParser()

    clParser.add_argument('-p', '--platform', dest="platform",
                          help="Platform to run on ('pi' for Raspi, 'win' for Windows)",
                          required=True)
    clParser.add_argument('-f', '--file', dest="filename", help="image file to process",
                          required=False)

    args = clParser.parse_args()

    if args.platform == 'pi':
        settings.on_raspy = True
    else:
        settings.on_raspy = False

    if args.platform == 'win':
        settings.on_win = True
    else:
        settings.on_win = False

    # create Beamer and Camera for taking picture and showing results
    miniBeamer = Beamer()
    raspiCam = Camera()

    # start Flask webserver in background
    webq = Queue()
    wserv = Webserver(webq)
    webThread = threading.Thread(target=wserv.run, daemon=True).start()

    # attach mouse callback to window for measuring
    #cv2.setMouseCallback("result", mouse_callback)

    # get image from file or camera
    if args.filename:
        """ Load image from disk if filename is given as parameter"""
        src = cv2.imread(args.filename, cv2.IMREAD_COLOR)
        # Check if image is loaded fine
        if src is None:
            raise GetImage('Error opening image!')
    else:
        """ give out white image with beamer and take picture"""
        miniBeamer.show_white()
        cv2.waitKey()
        # time.sleep(5)
        src = raspiCam.take_picture(1280, 720)
        if src is None:
            raise GetImage('Error taking picture!')

    if settings.debugging is True:
        cv2.namedWindow("source", cv2.WINDOW_NORMAL)
        cv2.imshow("source", src)
        cv2.waitKey(1)

    # find table
    found_table = Table.find_self(src, raspiCam.pix_per_mm, raspiCam.offset_x, raspiCam.offset_y)

    if found_table is None:
        print("No table in undistorted found!")

    while webq.get() == 'Start':
        # clear result image
        miniBeamer.clear_image()

        miniBeamer.add_object(found_table)

        # find balls
        found_balls = Ball.find_self(src, raspiCam.pix_per_mm, raspiCam.offset_x, raspiCam.offset_y)

        # add draw balls
        for ball in found_balls:
            # if(found_table.isInside(ball)):
            miniBeamer.add_object(ball)
            # print("ball found")

        miniBeamer.show_objects()

        cv2.imwrite("./web/static/result.jpg", miniBeamer.outPict)
        cv2.waitKey(1)
        #    if (cv2.waitKey(30) & 0xFF) == 27:
        #       break
        # cv2.waitKey()

    cv2.destroyAllWindows()
    return 0


if __name__ == '__main__':
    main()
