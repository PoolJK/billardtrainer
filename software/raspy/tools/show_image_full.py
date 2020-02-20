#!/usr/bin/python3
import cv2
import argparse

clParser = argparse.ArgumentParser()
clParser.add_argument('-f', '--file', dest="filename", help="image file to process",
                          required=False)

args = clParser.parse_args()

# cv2.WND_PROP_AUTOSIZE
cv2.namedWindow("beamer", cv2.WINDOW_AUTOSIZE + cv2.WINDOW_NORMAL)
cv2.setWindowProperty("beamer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
pict = cv2.imread(args.filename, cv2.IMREAD_COLOR)
print(pict.shape)
cv2.imshow("beamer", pict)
cv2.waitKey()
cv2.destroyAllWindows()
