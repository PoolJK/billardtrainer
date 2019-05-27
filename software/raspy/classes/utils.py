from threading import Lock
import time
import cv2
import numpy as np


# shorthand sleep
def wait(ms):
    time.sleep(ms / 1000)


# lock protected print in Threads
def lp(msg):
    lock = Lock()
    lock.acquire()
    print(msg)
    lock.release()


# empty method as callback for Trackbars
def nothing(_):
    pass


# time difference as int in [ms]
def dt(t1, t2):
    return int((t2 - t1) * 1000)


# current time
def now():
    return time.time()


# rotate an image keeping the full image
def rotate(image, angle):
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


# RGB
# colors = {
#     0: [255, 255, 255],
#     1: [200, 20, 10],
#     2: [240, 240, 20],
#     3: [10, 120, 40],
#     4: [100, 60, 55],
#     5: [0, 20, 230],
#     6: [200, 20, 200],
#     7: [10, 10, 10]
# }

# BGR
colors = {
    0: [255, 255, 255],
    1: [10, 20, 200],
    2: [20, 240, 240],
    3: [40, 120, 10],
    4: [55, 60, 100],
    5: [230, 20, 0],
    6: [200, 20, 200],
    7: [10, 10, 10]
}


# ball color from value
def ball_color(value):
    return colors.get(value, None)


def ball_value(color):
    for k, v in colors.items():
        if v == color:
            return k
    return 0
