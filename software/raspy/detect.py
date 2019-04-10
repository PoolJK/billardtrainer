import os
import cv2
import numpy as np

from classes.ball import Ball


class Detect:

    x_scale = 0
    y_scale = 0

    def __init__(self):
        pass

    def mouse_callback(self, x, y, flags, param):
        if self == cv2.EVENT_LBUTTONDOWN:
            # print(param.shape)
            # print('Coord screen: x={} y={}'.format(x, y))
            x = min(int(x * Detect.x_scale), param.shape[1] - 1)
            y = min(int(y * Detect.y_scale), param.shape[0] - 1)
            print("Coord image: {} {}, Value: {}".format(x, y, param[y, x, :]))

    @staticmethod
    def remove_background(image):
        # green RGB cloth mask
        upper_green = np.uint8([83, 170, 149])
        lower_green = np.uint8([26, 58, 33])
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mask = cv2.inRange(img_rgb, lower_green, upper_green)
        mask_inv = cv2.bitwise_not(mask)
        return cv2.bitwise_and(image, image, mask=mask_inv)

    def nothing(*x):
        pass

    def main(self, filename):
        cv2.namedWindow('out', cv2.WINDOW_NORMAL)
        cv2.namedWindow('hsv_mask', cv2.WINDOW_NORMAL)
        cv2.namedWindow('hsv')
        cv2.namedWindow('src')
        win_size = (800, 450)
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
        src = cv2.imread(filename)
        self.x_scale = src.shape[1] / win_size[0]
        self.y_scale = src.shape[0] / win_size[1]
        cv2.setMouseCallback('src', self.mouse_callback, src)
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
            gray_masked = cv2.bitwise_and(gray, gray, mask=mask)
            grad_val = max(cv2.getTrackbarPos('grad_val', 'out'), 1)
            acc_thr = max(cv2.getTrackbarPos('acc_thr', 'out'), 1)
            dp = max(cv2.getTrackbarPos('dp', 'out'), 1)
            min_dist = max(cv2.getTrackbarPos('min_dist', 'out'), 1)
            min_radius = cv2.getTrackbarPos('min_radius', 'out')
            max_radius = cv2.getTrackbarPos('max_radius', 'out')
            found_balls = Ball.find(gray_masked, dp, min_dist, grad_val, acc_thr, min_radius, max_radius)
            out = np.zeros(gray.shape, np.uint8)
            for ball in found_balls:
                ball.draw(out)
            out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
            out = cv2.addWeighted(src, 1, out, 1, 0)
            src_d = cv2.resize(src, win_size, interpolation=cv2.INTER_CUBIC)
            cv2.imshow('src', src_d)
            mask_d = cv2.resize(mask, win_size, interpolation=cv2.INTER_CUBIC)
            cv2.imshow('hsv_mask', mask_d)
            cv2.setMouseCallback('hsv', self.mouse_callback, hsv)
            hsv_d = cv2.resize(hsv, win_size, interpolation=cv2.INTER_CUBIC)
            cv2.imshow('hsv', hsv_d)
            cv2.imshow('out', out)
            cv2.resizeWindow('hsv_mask', win_size[0], win_size[1])
            cv2.resizeWindow('out', win_size[0], win_size[1])
            cv2.resizeWindow('hsv', win_size[0], win_size[1])
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            if key == ord('s'):
                if not os.path.isdir('resources/experimental/outputs'):
                    try:
                        os.makedirs('resources/experimental/outputs')
                    except OSError:
                        pass
                cv2.imwrite('resources/experimental/Video/out.jpg', out)
        cv2.destroyAllWindows()
        return 0

    @staticmethod
    def video_test():
        avg = np.ndarray.astype(cv2.imread('resources/experimental/Video/empty_average.jpg'), np.float)
        # avg = cv2.imread('resources/experimental/Video/empty_average.jpg')
        cap = cv2.VideoCapture('resources/experimental/Video/raw.mp4')
        fps = cap.get(cv2.CAP_PROP_FPS)
        n_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print('fps={} n_frames={} width={} height={}'.format(fps, n_frames, width, height))
        start_pos = 30*fps
        end_pos = 100*fps
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_pos)
        out = cv2.VideoWriter('resources/experimental/Video/test_out2.mp4',
                              cv2.VideoWriter_fourcc(*'mp4v'), 25, (int(width), int(height)))
        # frames = []
        # f_sum = np.zeros((height, width, 3), np.float)
        # while cap.isOpened():
        #     r, frame = cap.read()
        #     if r:
        #         cv2.imshow('video', frame)
        #         frames.append(frame)
        #         f_sum += frame
        #     # out.write(frame)
        #     if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q') or cap.get(cv2.CAP_PROP_POS_FRAMES) >= n_frames:
        #         break
        # avg = np.ndarray.astype(f_sum / len(frames), np.uint8)
        # cv2.imshow('avg', avg)
        # cv2.imwrite('resources/experimental/video/spots_average.jpg', avg)
        diff = np.zeros(avg.shape, np.float)
        size = (16, 9)
        #avg = cv2.resize(avg, size)
        while True and cap.get(cv2.CAP_PROP_POS_FRAMES) < end_pos:
            r, frame = cap.read()
            #frame = cv2.resize(frame, size)
            #print(frame)
            #print('frame min={} max={}'.format(frame.min(), frame.max()))
            #print(np.ndarray.astype(avg, int))
            #print('avg min={} max={}'.format(avg.min(), avg.max()))
            diff = frame - avg
            #print(diff[0, 0, :])
            #print('diff min={} max={}'.format(diff.min(), diff.max()))
            diff += abs(diff.min())
            diff *= 255/diff.max()
            #print('diff min={} max={}'.format(diff.min(), diff.max()))
            frame = np.ndarray.astype(diff, np.uint8)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            cv2.imshow('hsv', hsv)
            hsv[:, :, 2] = 255
            hsv = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            cv2.imshow('s=255', hsv)
            #print('frame min={} max={}'.format(frame.min(), frame.max()))
            cv2.imshow('video', frame)
            cv2.setMouseCallback('s=255', Detect.mouse_callback, hsv)
            out.write(hsv)
            if cv2.waitKey(int(fps/fps)) & 0xFF == ord('q'):
                break
            #break
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
