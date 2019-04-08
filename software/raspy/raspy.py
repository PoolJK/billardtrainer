#!/usr/bin/python3

import sys
import cv2
import numpy as np
from classes.table import Table
from classes.ball import Ball
from classes.camera import Camera

# some defaults, put in beamer class later
IMAGEWIDTH = 1280
IMAGEHEIGHT = 720

camera = Camera(cv2.CAP_DSHOW)


def mouse_callback(event, x, y, flags, param):
    """
    print coordinates of mouse cursor on terminal
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Coord: {} {}".format(x, y))


def main(args):
    pc_test = False
    if args.pc_test:
        pc_test = True
        # just in principle
        if args.use_ui and args.calibrate:
            camera.calibrate()
    if args.filename:
        # Load image from disk if filename is given as parameter
        src = cv2.imread(args.filename, cv2.IMREAD_COLOR)
        if src is None:
            print('Error opening image!')
            return 0
        cv2.imshow("Source Image", src)
        cv2.setMouseCallback("Source Image", mouse_callback)
        # create white image for output
        white = np.zeros((IMAGEHEIGHT, IMAGEWIDTH, 3), np.uint8)
        white[:] = (255, 255, 255)
        cv2.namedWindow("Beamer")
        # don't fullscreen it when on pc
        if not pc_test:
            cv2.setWindowProperty("Beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback("Beamer", mouse_callback)
    else:
        # give out white image with beamer as light source then take picture
        white = np.zeros((IMAGEHEIGHT, IMAGEWIDTH, 3), np.uint8)
        white[:] = (255, 255, 255)
        cv2.namedWindow("Beamer")
        # don't fullscreen it when on pc
        if not pc_test:
            cv2.setWindowProperty("Beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback("Beamer", mouse_callback)
        # draw marker for beamer adjustment
        # cv2.circle(white, (50,50), 15, (35, 35, 205), 3)
        # cv2.circle(white, (1230,50), 15, (35, 35, 205), 3)
        # cv2.circle(white, (1230,910), 15, (35, 35, 205), 3)
        # cv2.circle(white, (50,910), 15, (35, 35, 205), 3)

        camera.prepare_capture(cv2.CAP_DSHOW if pc_test else 0, IMAGEHEIGHT, IMAGEWIDTH)

        # show white image on beamer while taking picture
        cv2.imshow("Beamer", white)
        # do you have to wait here?
        cv2.waitKey(1)

        src = camera.pull_frame()

        # src can be an image or two images if the camera was calibrated
        if not type(src) == np.ndarray:
            uncalibrated_src = src['src']
            src = src['calibrated']
            cv2.imshow("Source Image", uncalibrated_src)
            cv2.imshow("Calibrated Source Image", src)
            cv2.setMouseCallback("Calibrated Source Image", mouse_callback)
        else:
            cv2.imshow("Source Image", src)
        cv2.setMouseCallback("Source Image", mouse_callback)
        camera.stop_capture()

    # resize and crop
    ratio = IMAGEWIDTH / IMAGEHEIGHT
    crop = int((src.shape[0] - src.shape[1] / ratio) * 0.5)
    src = src[crop:src.shape[0] - crop, :, :]
    src = cv2.resize(src, (IMAGEWIDTH, IMAGEHEIGHT), cv2.INTER_CUBIC)

    # create gray blurred image from source
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)
    if args.debug:
        cv2.imshow("blur", blur)

    # create black/white image to show found artifacts in
    output = np.zeros((IMAGEHEIGHT, IMAGEWIDTH), np.uint8)

    # find table
    found_table = Table.find(blur)
    if not found_table:
        print("no table found")
    else:
        # draw table
        found_table.draw_self(output)
        if args.debug:
            cv2.imshow("Found table", output)
            print("table: y: {}  y: {}  width: {}  height: {}  angle: {}"
                  .format(found_table.x, found_table.y, found_table.width, found_table.height, found_table.angle))

    # find balls
    found_balls = Ball.find(blur)
    # draw balls (inside table)
    for ball in found_balls:
        # if(found_table.isInside(ball)):
        ball.draw(output)

    if pc_test:
        output = cv2.cvtColor(output, cv2.COLOR_GRAY2BGR)
        output = cv2.addWeighted(src, 0.5, output, 0.5, 0)
    cv2.imshow("Beamer", output)
    cv2.waitKey()
    if not args.use_ui:
        cv2.destroyAllWindows()
    return 0
