import cv2
import numpy as np

frame_width = 16
frame_height = 9

cap = cv2.VideoCapture(0)

fail_count = 0
while frame_width < 4000 and fail_count < 10:
    r, img = cap.read()
    if not r:
        fail_count += 1
        continue
    print('setting height to {}: '.format(frame_height))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    print('setting width to {}: '.format(frame_width))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
