# interface during development
import cv2
from raspy import raspy


def main(args):
    n = int(input("Select image by number (1-5) or skip to use camera ") or 0)
    if 1 <= n <= 5:
        args.filename = 'resources/testimages/ball'+str(n)+'.jpg'
    args.calibrate = input("calibrate camera? (y) ") == 'y'
    raspy.main(args)
    if input("again? (y) ") == 'y':
        main(args)
    else:
        cv2.destroyAllWindows()
