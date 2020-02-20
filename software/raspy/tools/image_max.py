# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 16:44:27 2017
@author: sakurai
"""


import numpy as np
import cv2
import screeninfo

if __name__ == '__main__':

    is_color = False
    print(screeninfo.get_monitors())
    # get the size of the screen
    screen = screeninfo.get_monitors()[0]
    width, height = screen.width, screen.height
    
    print(width, height)

    # create image
    if is_color:
        image = np.ones((height, width, 3), dtype=np.float32)
        image[:10, :10] = 0  # black at top-left corner
        image[height - 10:, :10] = [1, 0, 0]  # blue at bottom-left
        image[:10, width - 10:] = [0, 1, 0]  # green at top-right
        image[height - 10:, width - 10:] = [0, 0, 1]  # red at bottom-right
    else:
        image = np.ones((height, width), dtype=np.float32)
        image[0, 0] = 0  # top-left corner
        image[height - 2, 0] = 0  # bottom-left
        image[0, width - 2] = 0  # top-right
        image[height - 2, width - 2] = 0  # bottom-right

    window_name = 'projector'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                          cv2.WINDOW_FULLSCREEN)
    cv2.imshow(window_name, image)
    cv2.waitKey()
    cv2.destroyAllWindows()