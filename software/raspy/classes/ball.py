from .utils import *
from . import settings


class Ball:
    """
    Parameters and functions for a billiard ball
    """

    # HoughCircles parameters
    p1 = 50
    p2 = 29
    minR = 16
    maxR = 28

    def __init__(self, x, y, radius=26, color=None, text=None):
        """
        Generate new ball
        :param x: x-position of center in mm
        :param y: y-position of center in mm
        :param radius: radius in mm
        :param color: ball color
        """
        if color is None:
            color = [255, 255, 255]
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.text = text

    def draw(self, image, offset_x, offset_y, ppm_x, ppm_y) -> None:
        screen_x = int((self.x - offset_x) * ppm_x)
        screen_y = int((self.y - offset_y) * ppm_y)
        # print('ball drawn @({}, {}) [px] ({}, {}) [mm]'.format(screen_x, screen_y, self.x, self.y))
        # circle fill
        cv2.circle(image, (screen_x, screen_y),
                   int(self.radius * ppm_x), self.color, -1)
        # circle outline white
        cv2.circle(image, (screen_x, screen_y),
                   int(self.radius * ppm_x), [255, 255, 255], 5)
        # draw mid point for debugging
        if settings.debug:
            cv2.drawMarker(image, (screen_x, screen_y),
                           [1-v for v in self.color], cv2.MARKER_CROSS, 10, 1)
        if self.text is not None:
            cv2.putText(image, self.text, (screen_x, screen_y),
                        cv2.FONT_HERSHEY_PLAIN, 3, [1-v for v in self.color], 5)

    @staticmethod
    def find(image, offs_x=0, offs_y=0, pix_per_mm=1):
        # create gray image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        rows = gray.shape[0]
        # print("{} {} {} {}".format(p1, p2, minR, maxR))

        # find circles in image
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=Ball.p1,
                                   param2=Ball.p2, minRadius=Ball.minR, maxRadius=Ball.maxR)
        # found circles with position in pixels relative from image origin in upper left corner
        balls = []
        if circles is not None:
            for i in circles[0, :]:
                # get relative position from image origin, convert to mm and subtract camera offset
                balls.append(Ball(((i[0] - (image.shape[1] / 2)) / pix_per_mm) - offs_x,
                                  ((i[1] - (image.shape[0] / 2)) / pix_per_mm) - offs_y,
                                  i[2] / pix_per_mm))
                if settings.debug:
                    print("ball found: x:{}, y:{} (mm)".format(((i[0] - (image.shape[1] / 2)) / pix_per_mm) - offs_x,
                                                               ((i[1] - (image.shape[0] / 2)) / pix_per_mm) - offs_y))
        return balls
