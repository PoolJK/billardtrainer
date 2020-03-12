#!/usr/bin/python3

import argparse
import sys
import cv2
import threading
from queue import Queue
import settings
from beamer import Beamer
from camera import Camera
from web.webserv import Webserver
from detector import Detector
from less_eck_pos import EckertPositoinDrill


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

    dectsem = threading.Semaphore()
    # start object detector in background
    if args.filename:
        detect = Detector(semaphore=dectsem, cam=None, filename=args.filename)

    else:
        detect = Detector(semaphore=dectsem, cam=raspiCam)

    dectThread = threading.Thread(target=detect.run, daemon=True).start()

    less1 = EckertPositoinDrill()

    # wait for web server form action
    action = webq.get()
    while action is not 'Stop':
        if action == 'Start':
            # show new image
            miniBeamer.clear_image()
            miniBeamer.add_objects(detect.get_objects())
            miniBeamer.show_objects()
            # write new image for webserver
            cv2.imwrite("./web/static/result.jpg", miniBeamer.outPict)
            cv2.waitKey(1)
            #    if (cv2.waitKey(30) & 0xFF) == 27:
            #       break
            # cv2.waitKey()
        elif action == 'lesson1':
            # show new image
            miniBeamer.clear_image()
            miniBeamer.add_objects(less1.get_objects())
            miniBeamer.show_objects()
            # write new image for webserver
            cv2.imwrite("./web/static/result.jpg", miniBeamer.outPict)
            cv2.waitKey(1)

        action = webq.get()

    cv2.destroyAllWindows()
    return 0


if __name__ == '__main__':
    main()
