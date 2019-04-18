from threading import Lock
import time
import cv2
import numpy as np


def wait(ms):
    time.sleep(ms / 1000)


def lp(msg):
    # lock protected print in Threads
    lock = Lock()
    lock.acquire()
    print(msg)
    lock.release()


def dt(t1, t2):
    # time difference as int in [ms]
    return int((t2-t1)*1000)


def now():
    # current time
    return time.time()


def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    m = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(m[0, 0])
    sin = np.abs(m[0, 1])

    # compute the new bounding dimensions of the image
    n_w = int((h * sin) + (w * cos))
    n_h = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    m[0, 2] += (n_w / 2) - cX
    m[1, 2] += (n_h / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, m, (n_w, n_h), borderValue=(255, 255, 255))