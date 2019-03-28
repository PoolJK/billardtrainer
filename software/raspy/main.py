import cv2
import numpy as np

# set true if running tests on pc
ALGOTEST = True
# some defaults, put in beamer class later
IMAGEWIDTH = 1280
IMAGEHEIGHT = 960


def mouse_callback(event, x, y, flags, param):
    """
    print coordinates of mouse cursor on terminal
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Coord: {} {}".format(x, y))


def main(argv):
    tablecorners = np.zeros(shape=(4 ,2))
    tableangle = 0.0
    xStretch = 1.5
    yStretch = 1.2

    if not ALGOTEST:
        # create white image for beamer as light source
        white = np.zeros((IMAGEHEIGHT, IMAGEWIDTH, 3), np.uint8)
        white[:] = (255 ,255 ,255)
        cv2.namedWindow("beamer", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback("beamer", mouse_callback)
        # draw marker for beamer adjustment
        # cv2.circle(white, (50,50), 15, (35, 35, 205), 3)
        # cv2.circle(white, (1230,50), 15, (35, 35, 205), 3)
        # cv2.circle(white, (1230,910), 15, (35, 35, 205), 3)
        # cv2.circle(white, (50,910), 15, (35, 35, 205), 3)

        # show white image on beamer while taking picture
        cv2.imshow("beamer", white)
        cv2.waitKey()
        # time.sleep(5)

    # image to show found artefacts in
    outPict= np.zeros((IMAGEHEIGHT, IMAGEWIDTH), np.uint8)

    if ALGOTEST:
        # Load an image from disk
        default_file = "ball1.jpg"
        filename = argv[0] if len(argv) > 0 else default_file
        src = cv2.imread(default_file, cv2.IMREAD_COLOR)
        # Check if image is loaded fine
        if src is None:
            print ('Error opening image!')
            print ('Usage: hough_lines.py [image_name -- default ' + default_file + '] \n')
            return -1

    else:
        # take picture from camera
        capture = cv2.VideoCapture(0)
        if not capture.isOpened:
            print("Error access camera!")
            return -1

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGEWIDTH);
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGEHEIGHT)

        has_frame, src = capture.read()
        if not has_frame:
            print("Error taking picture")
            return -1

    # create gray image
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)


if __name__ == "__main__":
    main(sys.argv[1:])