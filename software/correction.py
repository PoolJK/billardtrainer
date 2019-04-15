
import os
import cv2
import math
import numpy as np

src = cv2.imread('resources/snook2b.jpg')
src2 = src
cv2.namedWindow('src', cv2.WINDOW_NORMAL)
cv2.imshow('src', src)
k = cv2.waitKey(0)

if k == 27:         # wait for ESC key to exit
    cv2.destroyAllWindows()
elif k == ord('s'): # wait for 's' key to save and exit
    cv2.imwrite('resources/Bild.jpg',src)
    cv2.destroyAllWindows()

# input
strength = 3.4 # strength as floating point >= 0. 0 = no change, high numbers equal stronger correction.
zoom = 1.3    # as floating point >= 1.(1 = no change in zoom)

# algorithm
imageHeight, imageWidth, imageChannels = src.shape
print (src.shape)
src2= np.zeros((imageHeight, imageWidth, 3), np.uint8)
src2[:] = (255, 255, 255)

halfWidth  = imageWidth / 2
halfHeight = imageHeight / 2

if strength == 0:
    strength = 0.00001

correctionRadius = math.sqrt(math.pow(imageWidth,2) + math.pow(imageHeight,2)) / strength
print (correctionRadius)

n=0;
for x in range(imageWidth):
    for y in range(imageHeight):
        newX = x - halfWidth
        newY = y - halfHeight
        distance = math.sqrt(math.pow(newX,2) + math.pow(newY,2))
        r = distance / correctionRadius
        if r == 0:
            theta = 1
        else:
            theta = math.atan(r)/r

        sourceX = int(halfWidth + theta * newX * zoom)
        sourceY = int(halfHeight + theta * newY * zoom)
        if sourceX < imageWidth:
            if sourceY < imageHeight:
                (b, g, r) = src[sourceY, sourceX]
                src2[y, x] = (b, g, r)

        n+=1

print(n)

cv2.namedWindow('correction', cv2.WINDOW_NORMAL)
cv2.imshow('correction', src2)
b = cv2.waitKey(0)

if b == 27:         # wait for ESC key to exit
    cv2.destroyAllWindows()
elif b == ord('s'): # wait for 's' key to save and exit
    cv2.imwrite('resources/Bild1.jpg',src)
    cv2.destroyAllWindows()