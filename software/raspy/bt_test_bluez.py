from software.classes.bluetooth import BT
from imutils.video import VideoStream
from software.classes.utils import *


def run_test():
    bluetooth = BT()
    while True:
        msg = bluetooth.read()
        print(msg)
        if msg == "exit":
            break
    # vs = VideoStream(usePiCamera=True, resolution=(1280, 720), framerate=60).start()
    # vs.camera.iso = 1600
    # print("1280x720@90")
    # wait(2000)
    # vs.camera.shutter_speed = vs.camera.exposure_speed
    # vs.camera.exposure_mode = 'off'
    # g = vs.camera.awb_gains
    # vs.camera.awb_mode = 'off'
    # vs.camera.awb_gains = g
    # fps = 0
    # start = now()
    # while True:
    #     fps += 1
    #     if dt(start, now()) >= 1000:
    #         print(dt(start, now()), end='')
    #         print('{: 2d}'.format(fps), end='\r')
    #         fps = 0
    #         start = now()
    #     frame = vs.read()
    #     cv2.imshow('src', frame)
    #     key = cv2.waitKey(1) & 0xFF
    #     if key == ord('q'):
    #         break
    # print('\n')
    # cv2.destroyAllWindows()
    # vs.stop()
