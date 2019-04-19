"""
@file detect_test.py
@brief This program demonstrates detection of balls and table contours
"""
import sys
import time
import math
import cv2
import numpy as np


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Coord: {} {}".format(x, y))


# image is expected be in RGB color space
def remove_backgr(image):
    # green RGB cloth mask
    upper_green = np.uint8([83, 170, 149])
    lower_green = np.uint8([26, 58, 33])
    imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mask = cv2.inRange(imgRGB, lower_green, upper_green)
    mask_inv = cv2.bitwise_not(mask)
    return cv2.bitwise_and(image, image, mask=mask_inv)


def main(argv):
    tablecorners = np.zeros(shape=(4,2))
    tableangle = 0.0
    xStretch = 1.5
    yStretch = 1.2
    
    #show white image to light table
    #white = cv2.imread("white.jpg")
    white = np.zeros((960, 1280, 3), np.uint8)
    white[:] = (255,255,255)
    print(white.shape)
    cv2.namedWindow("beamer", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback("beamer", mouse_callback)
     #draw marker for picture adjustment
    """
    cv2.circle(white, (50,50), 15, (35, 35, 205), 3)
    cv2.circle(white, (1230,50), 15, (35, 35, 205), 3)
    cv2.circle(white, (1230,910), 15, (35, 35, 205), 3)
    cv2.circle(white, (50,910), 15, (35, 35, 205), 3)
    """
    cv2.imshow("beamer", white)
    cv2.waitKey()
    #time.sleep(5)
    
    #image to show found artefacts in
    outPict= np.zeros((960, 1280), np.uint8)
   
    
    """
    # Loads an image
    default_file = "ball1.jpg"
    filename = argv[0] if len(argv) > 0 else default_file
    src = cv2.imread(default_file, cv2.IMREAD_COLOR)
    # Check if image is loaded fine
    if src is None:
        print ('Error opening image!')
        print ('Usage: hough_lines.py [image_name -- default ' + default_file + '] \n')
        return -1
    """
    capture = cv2.VideoCapture(0)
    if not capture.isOpened:
        print("Error access camera!")
        return -1
    #capture.set(cv2.CAP_PROP_FRAME_WIDTH, 3280)
    #capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 2464)
    #capture.set(cv2.CAP_PROP_FRAME_WIDTH, 2592)
    #capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1944)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)

    has_frame, src = capture.read()
    if not has_frame:
        print("Error taking picture")
        return -1

    """
    panel = np.zeros([100, 700], np.uint8)
    cv2.namedWindow('panel')

    def nothing(x):
        pass

    cv2.createTrackbar('param1', 'panel', 1, 255, nothing)
    cv2.createTrackbar('param2', 'panel', 1, 255, nothing)
    cv2.createTrackbar('minRadius', 'panel', 1, 255, nothing)
    cv2.createTrackbar('maxRadius', 'panel', 1, 255, nothing)

    cv2.setTrackbarPos ('param1', 'panel', 50)
    cv2.setTrackbarPos ('param2', 'panel', 20)
    cv2.setTrackbarPos ('minRadius', 'panel', 1)
    cv2.setTrackbarPos ('maxRadius', 'panel', 30)
    """

    #remove the background color
    #image= remove_backgr(src)
    #cv2.imshow("Background removed", image)

    #canny = cv2.Canny(src, 50, 200, None, 3)
    #cv2.imshow("Canny", canny)

    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    #cv2.imshow("gray blur", gray)

    #while True:
    """
    p1 = cv2.getTrackbarPos('param1', 'panel')
    if p1 < 1: p1 = 1
    p2 = cv2.getTrackbarPos('param2', 'panel')
    if p2 < 1: p2 = 1
    minR = cv2.getTrackbarPos('minRadius', 'panel')
    if minR < 1: minR = 1
    maxR = cv2.getTrackbarPos('maxRadius', 'panel')
    if maxR < 1: maxR = 1
    """
    
    """ find balls
    """
    p1 = 50
    p2 = 29
    minR = 16
    maxR = 28
    rows = gray.shape[0]
    #print("{} {} {} {}".format(p1, p2, minR, maxR))

    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=p1, param2=p2, minRadius=minR, maxRadius=maxR)
    #circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=50, param2=20, minRadius=1, maxRadius=30)

    #cv2.rectangle(src, (150, 220), (1150, 800), (100, 100, 200), 3)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            #center = (i[0], i[1])
            #only circles inside table
            if(center[1] > 220):
                print("Circle at: {}".format(center))
                # circle center
                cv2.circle(outPict, center, 1, (0, 100, 100), 3)
                # circle outline
                radius = i[2] + 10
                cv2.circle(outPict, center, radius, (255, 0, 255), 3)
                cv2.circle(src, center, radius, (255, 0, 255), 3)


    """ find table
    """
    _, thresh = cv2.threshold(gray, 100, 255, 0)
    #thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    #binary = cv2.bitwise_not(gray)
    #cv2.imshow("thresh", thresh)
    #_, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        (x, y), (w, h), angle = cv2.minAreaRect(contour)
        if w > 300 and h > 200:
            #convert x, y w, h, angle to four points of rectangle
            #box = cv2.boxPoints(((x, y), (w * xStretch, h * yStretch), angle))
            box = cv2.boxPoints(((x, y), (w, h), angle))
            print("Rectangle at: {},{}, with size: {},{}, angle: {}".format(x, y, w, h, angle))
            tableangle = angle
            # convert to integer
            box = np.int0(box)
            table = np.copy(box)
            #print(table)
            #print(box)
            cv2.drawContours(outPict, [box], 0 , (255, 0, 255), 2)
            cv2.drawContours(src, [box], 0 , (255, 0, 255), 2)

    #rotate table to 90 degrees
    if tableangle < -45.0:
        tableangle = (90.0 + tableangle)
        # otherwise, just take the inverse of the angle to make it positive
    else:
        tableangle = -tableangle

    """
    # rotate the image to deskew it
    (h, w) = outPict.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, tableangle, 1.0)
    rotated = cv2.warpAffine(outPict, M, (w, h), flags = cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    """
    #print(table)
    pts_dst = np.array([ [1230, 910], [50, 910], [50, 50], [1230, 50] ])
    pts_src = np.array([ table[0],table[1],table[2], table[3] ])

    # Calculate the homography
    h, _ = cv2.findHomography(pts_src, pts_dst)

    # Warp source image to destination
    im_dst = cv2.warpPerspective(outPict, h, (outPict.shape[1], outPict.shape[0]))
    
    #cv2.imshow("detected", src)
    # rotsize = cv2.resize(rotated, (0,0), fx=1.7, fy=1.2, interpolation=cv2.INTER_LINEAR)
    #cv2.imshow("source", src)
    cv2.imshow("beamer", im_dst)
    
    #    if (cv2.waitKey(30) & 0xFF) == 27:
    #       break

    cv2.waitKey()
    cv2.destroyAllWindows()
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])
