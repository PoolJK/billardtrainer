# interface during development

import cv2

from raspy import detect_test
# from classes.camera import Camera


def main(args):
    # n = int(input("Select image by number (1-5) or skip to use camera ") or 0)
    # if 1 <= n <= 5:
    #     args.filename = 'resources/testimages/ball'+str(n)+'.jpg'
    # Camera(cv2.CAP_DSHOW).show_video()
    args.__setattr__('calibrate_cam', True)  # input("calibrate camera? (y) ") == 'y')
    # camera = Camera(cv2.CAP_DSHOW)
    # camera.calibrate_cam()

    detect_test.main(args.filename)
    # detect_test.further_test()

    # raspy.main(args)
    # print("(r): run from start")
    # print("(any): quit")
    # key = cv2.waitKey() & 0xFF
    cv2.destroyAllWindows()
    # if key == ord('r'):
    #    main(args)
