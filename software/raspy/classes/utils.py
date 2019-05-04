import time
import cv2
import numpy as np


def wait(ms):
    """
    Shorthand for time.sleep
    :param ms: time in milliseconds
    """
    time.sleep(ms / 1000)


def nothing(*x):
    """
    Empty method as callback for OpenCV-trackbars
    """
    pass


def now():
    """
    Shorthand for time.time()
    :returns: current time (in seconds since unix epoch, I think)
    """
    return time.time()


def time_diff(t1, t2=now()):
    """
    Get time difference between starting time t1 and either t2 or current time
    :param t1: start of interval
    :param t2: end of interval or current time if None
    :returns: time difference in ms
    """
    return int((t2 - t1) * 1000)


def rotate_bound(image, angle):
    """
    Rotate an image without cutting of corners
    :param image: image to rotate
    :param angle: angle to rotate to
    :returns: the rotated image (with padded white)
    """
    # grab the dimensions of the image and then determine the center
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
