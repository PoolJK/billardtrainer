#!/usr/bin/python3

import cv2
import math
import numpy as np
import time


def scale(val):
    return round((val / 25.5) + 0.001, 3)


def nothing(*x):
    pass


def correct():
    src = cv2.imread('resources/testimages/snook4b.jpg')
    src = cv2.resize(src, (int(src.shape[1]/4), int(src.shape[0]/4)), cv2.INTER_CUBIC)
    cv2.namedWindow('src', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('src', 480, 800)
    cv2.namedWindow('correction', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('correction', 480, 800)
    cv2.imshow('src', src)

    # algorithm
    image_height, image_width, image_channels = src.shape
    print('src.shape={}'.format(src.shape))
    src2 = np.zeros(src.shape, np.uint8)
    src2[:] = (255, 255, 255)  # TODO: needed?

    half_width = image_width / 2
    half_height = image_height / 2

    cv2.createTrackbar('strength', 'correction', 126, 255, nothing)
    cv2.createTrackbar('zoom', 'correction', 45, 255, nothing)

    corr_r_base = math.sqrt(math.pow(image_width, 2) + math.pow(image_height, 2))
    while True:
        start = time.time()
        n = 0
        zoom = scale(cv2.getTrackbarPos('zoom', 'correction'))
        strength = scale(cv2.getTrackbarPos('strength', 'correction'))
        correction_radius = corr_r_base / strength
        print('zoom={} strength={} correction_radius={}'.format(zoom, strength, correction_radius))
        for x in range(image_width):
            for y in range(image_height):
                new_x = x - half_width
                new_y = y - half_height
                distance = math.sqrt(math.pow(new_x, 2) + math.pow(new_y, 2))
                if distance == 0:
                    theta = 1
                else:
                    r = distance / correction_radius
                    theta = math.atan(r)/r
                source_x = int(half_width + theta * new_x * zoom)
                source_y = int(half_height + theta * new_y * zoom)
                if source_x < image_width and source_y < image_height:
                    (b, g, r) = src[source_y, source_x]
                else:
                    (b, g, r) = (0, 0, 0)
                src2[y, x] = (b, g, r)
                n += 1
        print(n)

        cv2.imshow('correction', src2)
        end = time.time()
        print('calc time = {}'.format(end - start))
        key = cv2.waitKey()

        if key == 27:  # wait for ESC key to exit
            break
        elif key == ord('s'):  # wait for 's' key to save
            cv2.imwrite('resources/correction_out.jpg', src2)
    cv2.destroyAllWindows()
    exit(0)


correct()
