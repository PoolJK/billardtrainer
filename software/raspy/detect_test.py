import os
import time
import cv2
import numpy as np

from classes.ball import Ball
from classes.camera import Camera


class DetectTest:

    x_scale = 0
    y_scale = 0
    camera = None
    win_size = None
    debug = False

    def __init__(self, args):
        if args.debug:
            self.debug = True
        # get display resolution
        if args.res:
            x, y = 0, 0
            if ',' in args.res:
                x, y = args.res.split(',')
            elif 'x' in args.res:
                x, y = args.res.split('x')
            else:
                print('bad resolution format, use 1280,720 or 1280x720')
                exit(0)
            self.win_size = (int(x), int(y))
        # set up camera (and calibrate)
        self.camera = Camera(args, self.win_size)

    def mouse_callback(self, event, x, y, flags, param):
        # on left mouse clock, print coordinates and image value
        if self == cv2.EVENT_LBUTTONDOWN:
            # print(param.shape)
            # print('Coord screen: x={} y={}'.format(x, y))
            x = min(int(x * DetectTest.x_scale), param.shape[1] - 1)
            y = min(int(y * DetectTest.y_scale), param.shape[0] - 1)
            print("Coord image: {} {}, Value: {}".format(x, y, param[y, x, :]))

    # currently not in use
    @staticmethod
    def remove_background(image):
        # green RGB cloth mask
        upper_green = np.uint8([83, 170, 149])
        lower_green = np.uint8([26, 58, 33])
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mask = cv2.inRange(img_rgb, lower_green, upper_green)
        mask_inv = cv2.bitwise_not(mask)
        return cv2.bitwise_and(image, image, mask=mask_inv)

    # empty method as callback for Trackbars
    def nothing(*x):
        pass

    def main(self):
        print('starting main(){}, \'x\' to quit, \'s\' to save output frame'
              .format(' in debug mode' if self.debug else ''))
        cv2.namedWindow('out', cv2.WINDOW_NORMAL)
        cv2.namedWindow('hsv_mask', cv2.WINDOW_NORMAL)
        cv2.namedWindow('hsv', cv2.WINDOW_NORMAL)
        cv2.namedWindow('src', cv2.WINDOW_NORMAL)
        cv2.createTrackbar('grad_val', 'out', 27, 255, self.nothing)
        cv2.createTrackbar('acc_thr', 'out', 48, 255, self.nothing)
        cv2.createTrackbar('min_dist', 'out', 28, 255, self.nothing)
        cv2.createTrackbar('dp', 'out', 2, 255, self.nothing)
        cv2.createTrackbar('min_radius', 'out', 11, 255, self.nothing)
        cv2.createTrackbar('max_radius', 'out', 19, 255, self.nothing)
        cv2.createTrackbar('h_lower', 'hsv_mask', 0, 255, self.nothing)
        cv2.createTrackbar('s_lower', 'hsv_mask', 0, 255, self.nothing)
        cv2.createTrackbar('v_lower', 'hsv_mask', 0, 255, self.nothing)
        cv2.createTrackbar('h_upper', 'hsv_mask', 255, 255, self.nothing)
        cv2.createTrackbar('s_upper', 'hsv_mask', 255, 255, self.nothing)
        cv2.createTrackbar('v_upper', 'hsv_mask', 255, 255, self.nothing)
        while True:
            start = time.time()
            src = self.camera.pull_cal_frame()
            srctime = int((time.time()-start)*1000)
            if src is None:
                print('error in main: couldn\'t read from src')
                return 0
            # calculate scales for mouse_callback
            self.x_scale = src.shape[1] / self.win_size[0]
            self.y_scale = src.shape[0] / self.win_size[1]
            cv2.setMouseCallback('src', self.mouse_callback, src)
            gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)
            hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
            lower = np.array([cv2.getTrackbarPos('h_lower', 'hsv_mask'), cv2.getTrackbarPos('s_lower', 'hsv_mask'),
                              cv2.getTrackbarPos('v_lower', 'hsv_mask')])
            upper = np.array([cv2.getTrackbarPos('h_upper', 'hsv_mask'), cv2.getTrackbarPos('s_upper', 'hsv_mask'),
                              cv2.getTrackbarPos('v_upper', 'hsv_mask')])
            # Threshold the HSV image
            mask = cv2.inRange(hsv, lower, upper)
            # Bitwise-AND mask and original image
            gray_masked = cv2.bitwise_and(gray, gray, mask=mask)
            # get parameters for hough_circle detection
            grad_val = max(cv2.getTrackbarPos('grad_val', 'out'), 1)
            acc_thr = max(cv2.getTrackbarPos('acc_thr', 'out'), 1)
            dp = max(cv2.getTrackbarPos('dp', 'out'), 1)
            min_dist = max(cv2.getTrackbarPos('min_dist', 'out'), 1)
            min_radius = cv2.getTrackbarPos('min_radius', 'out')
            max_radius = cv2.getTrackbarPos('max_radius', 'out')
            # run detection
            found_balls = Ball.find(gray_masked, dp, min_dist, grad_val, acc_thr, min_radius, max_radius)
            out = np.zeros(gray.shape, np.uint8)
            for ball in found_balls:
                ball.draw(out)
            # overlay contours over source image
            out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
            out = cv2.addWeighted(src, 1, out, 1, 0)
            # display (and resize) all windows
            src_d = cv2.resize(src, self.win_size, cv2.INTER_CUBIC)
            cv2.imshow('src', src_d)
            mask_d = cv2.resize(mask, self.win_size, cv2.INTER_CUBIC)
            cv2.imshow('hsv_mask', mask_d)
            cv2.setMouseCallback('hsv', self.mouse_callback, hsv)
            hsv_d = cv2.resize(hsv, self.win_size, cv2.INTER_CUBIC)
            cv2.imshow('hsv', hsv_d)
            out_d = cv2.resize(out, self.win_size, cv2.INTER_CUBIC)
            cv2.imshow('out', out_d)
            cv2.imshow('xsrc', cv2.resize(self.camera.pull_frame(), self.win_size))
            cv2.resizeWindow('hsv_mask', self.win_size[0], self.win_size[1])
            cv2.resizeWindow('out', self.win_size[0], self.win_size[1])
            cv2.resizeWindow('hsv', self.win_size[0], self.win_size[1])
            if self.debug:
                print('\rmain loop time: {}ms, read src took {}ms'
                      .format(int((time.time()-start)*1000), srctime), end='')
            key = cv2.waitKey(1) & 0xFF
            if key == ord('x'):
                print('')
                break
            if key == ord('s'):
                # save current frame to disk
                if not os.path.isdir('resources/experimental/outputs'):
                    try:
                        os.makedirs('resources/experimental/outputs')
                    except OSError:
                        pass
                cv2.imwrite('resources/experimental/Video/out.jpg', out)
            if key == 27:
                # ESC = exit
                print('bye')
                self.camera.stop_capture()
                cv2.destroyAllWindows()
                exit(0)
        self.camera.stop_capture()
        cv2.destroyAllWindows()
        return 0

    @staticmethod
    def video_test(filename=None):
        if filename:
            cap = cv2.VideoCapture(filename)
        else:
            cap = cv2.VideoCapture('resources/experimental/Video/rolling.mp4')
        fps = cap.get(cv2.CAP_PROP_FPS)
        n_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print('fps={} n_frames={} width={} height={}'.format(fps, n_frames, width, height))
        start_pos = 0
        end_pos = n_frames
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_pos)
        out = cv2.VideoWriter('resources/experimental/Video/test_out3.mp4',
                              cv2.VideoWriter_fourcc(*'mp4v'), 25, (int(width), int(height)))
        while cap.isOpened():
            r, frame = cap.read()
            if r:
                cv2.imshow('video', frame)
                # out.write(frame)
            if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q') or cap.get(cv2.CAP_PROP_POS_FRAMES) >= end_pos:
                break
        while True and cap.get(cv2.CAP_PROP_POS_FRAMES) < end_pos:
            r, frame = cap.read()
            # frame = cv2.resize(frame, size)
            # print(frame)
            # print('frame min={} max={}'.format(frame.min(), frame.max()))
            # print(np.ndarray.astype(avg, int))
            # print('avg min={} max={}'.format(avg.min(), avg.max()))
            # diff = frame - avg
            # print(diff[0, 0, :])
            # print('diff min={} max={}'.format(diff.min(), diff.max()))
            # diff += abs(diff.min())
            # diff *= 255/diff.max()
            # print('diff min={} max={}'.format(diff.min(), diff.max()))
            # frame = np.ndarray.astype(diff, np.uint8)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            cv2.imshow('hsv', hsv)
            hsv[:, :, 2] = 255
            hsv = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            cv2.imshow('s=255', hsv)
            # print('frame min={} max={}'.format(frame.min(), frame.max()))
            cv2.imshow('video', frame)
            cv2.setMouseCallback('s=255', DetectTest.mouse_callback, hsv)
            out.write(hsv)
            if cv2.waitKey(int(fps/fps)) & 0xFF == ord('q'):
                break
            # break
        cap.release()
        out.release()
        cv2.destroyAllWindows()

    @staticmethod
    def further_test(self):
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
