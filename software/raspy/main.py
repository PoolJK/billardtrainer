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


class GetImage(Exception):
    def __init__(self, msg):
        print(msg)
        # cv2.destroyAllWindows()
        sys.exit(-1)


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

    while webq.get() == 'Start':
        # clear result image
        miniBeamer.clear_image()

        miniBeamer.add_objects(detect.get_objects())

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
