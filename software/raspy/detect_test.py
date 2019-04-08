import os
import cv2
import numpy as np

from classes.ball import Ball


def __init__():
    pass


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # print(param.shape)
        scale = 6.64
        x = min(int(x * scale), param.shape[1])
        y = min(int(y * scale), param.shape[0])
        print("Coord: {} {}, Value: {}".format(x, y, param[y, x, :]))


# image is expected be in RGB color space
def remove_background(image):
    # green RGB cloth mask
    upper_green = np.uint8([83, 170, 149])
    lower_green = np.uint8([26, 58, 33])
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mask = cv2.inRange(img_rgb, lower_green, upper_green)
    mask_inv = cv2.bitwise_not(mask)
    return cv2.bitwise_and(image, image, mask=mask_inv)


def nothing(x):
    pass


def main(filename):
    cv2.namedWindow('out', cv2.WINDOW_NORMAL)
    cv2.namedWindow('hsv_mask', cv2.WINDOW_NORMAL)
    cv2.namedWindow('hsv')
    cv2.namedWindow('src')
    win_size = (800, 450)
    cv2.createTrackbar('grad_val', 'out', 123, 255, nothing)
    cv2.createTrackbar('acc_thr', 'out', 104, 255, nothing)
    cv2.createTrackbar('min_dist', 'out', 222, 255, nothing)
    cv2.createTrackbar('dp', 'out', 5, 255, nothing)
    cv2.createTrackbar('min_radius', 'out', 96, 255, nothing)
    cv2.createTrackbar('max_radius', 'out', 103, 255, nothing)
    cv2.createTrackbar('h_lower', 'hsv_mask', 58, 255, nothing)
    cv2.createTrackbar('s_lower', 'hsv_mask', 0, 255, nothing)
    cv2.createTrackbar('v_lower', 'hsv_mask', 35, 255, nothing)
    cv2.createTrackbar('h_upper', 'hsv_mask', 65, 255, nothing)
    cv2.createTrackbar('s_upper', 'hsv_mask', 255, 255, nothing)
    cv2.createTrackbar('v_upper', 'hsv_mask', 255, 255, nothing)
    src = cv2.imread(filename)
    scale = src.shape[0] / win_size[1]
    # print(scale)
    cv2.setMouseCallback('src', mouse_callback, src)
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    while True:
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        lower = np.array([cv2.getTrackbarPos('h_lower', 'hsv_mask'), cv2.getTrackbarPos('s_lower', 'hsv_mask'),
                          cv2.getTrackbarPos('v_lower', 'hsv_mask')])
        upper = np.array([cv2.getTrackbarPos('h_upper', 'hsv_mask'), cv2.getTrackbarPos('s_upper', 'hsv_mask'),
                          cv2.getTrackbarPos('v_upper', 'hsv_mask')])
        # red: (0,210,21)-(8,255,255)
        # Threshold the HSV image
        # print('lower={} upper={}'.format(lower, upper))
        mask = cv2.inRange(hsv, lower, upper)
        # Bitwise-AND mask and original image
        src_masked = cv2.cvtColor(cv2.bitwise_and(src, src, mask=mask), cv2.COLOR_BGR2GRAY)
        grad_val = max(cv2.getTrackbarPos('grad_val', 'out'), 1)
        acc_thr = max(cv2.getTrackbarPos('acc_thr', 'out'), 1)
        dp = max(cv2.getTrackbarPos('dp', 'out'), 1)
        min_dist = max(cv2.getTrackbarPos('min_dist', 'out'), 1)
        min_radius = cv2.getTrackbarPos('min_radius', 'out')
        max_radius = cv2.getTrackbarPos('max_radius', 'out')
        found_balls = Ball.find(src_masked, dp, min_dist, grad_val, acc_thr, min_radius, max_radius)
        out = np.zeros(gray.shape, np.uint8)
        for ball in found_balls:
            ball.draw(out)
        out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
        out = cv2.addWeighted(src, 1, out, 1, 0)
        srcd = cv2.resize(src, win_size, interpolation=cv2.INTER_CUBIC)
        cv2.imshow('src', srcd)
        maskd = cv2.resize(mask, win_size, interpolation=cv2.INTER_CUBIC)
        cv2.imshow('hsv_mask', maskd)
        cv2.setMouseCallback('hsv', mouse_callback, hsv)
        hsvd = cv2.resize(hsv, win_size, interpolation=cv2.INTER_CUBIC)
        cv2.imshow('hsv', hsvd)
        cv2.imshow('out', out)
        cv2.resizeWindow('hsv_mask', win_size[0], win_size[1])
        cv2.resizeWindow('out', win_size[0], win_size[1])
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('s'):
            if not os.path.isdir('resources/experimental/outputs'):
                try:
                    os.makedirs('resources/experimental/outputs')
                except OSError:
                    pass
            cv2.imwrite('resources/experimental/outputs/out.jpg', out)
    cv2.destroyAllWindows()
    return 0


def further_test():
    # 1. take image of table without balls on it
    # 2. take image of table with balls on it
    # 3. calculate absdiff (+noisefilter, blur, erode etc) yielding only the balls as imagedata
    #    absdiff makes balls appear colorshifted, but is necessary for detection of black ball,
    win_size = (800, 450)
    blank = cv2.imread('resources/experimental/blank.jpg')
    spots = cv2.imread('resources/experimental/spots.jpg')
    # blank = cv2.cvtColor(blank, cv2.COLOR_BGR2HSV)
    # spots = cv2.cvtColor(spots, cv2.COLOR_BGR2HSV)
    spotsd = cv2.absdiff(spots, blank)
    blankd = cv2.resize(blank, win_size, cv2.INTER_CUBIC)
    spotsd = cv2.resize(spotsd, win_size, cv2.INTER_CUBIC)
    cv2.imshow('blank', blankd)
    cv2.imshow('spots', spotsd)
    cv2.waitKey()
