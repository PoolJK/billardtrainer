from .utils import *
from . import settings


class Ball:
    """
    Parameters and functions for a billiard ball
    """

    # HoughCircles parameters
    grad_val = 90
    acc_thr = 67
    dp = 2
    min_dist = 100
    min_radius = 0
    max_radius = 100

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
        # cv2.circle(image, (screen_x, screen_y),
        #            int(self.radius * ppm_x), self.color, -1)
        # circle outline white
        cv2.circle(image, (screen_x, screen_y),
                   int(self.radius * ppm_x), [255, 255, 255], 5)
        # draw mid point for debugging
        if settings.debug:
            cv2.drawMarker(image, (screen_x, screen_y),
                           [1 - v for v in self.color], cv2.MARKER_CROSS, 10, 1)
        if self.text is not None:
            cv2.putText(image, self.text, (screen_x, screen_y),
                        cv2.FONT_HERSHEY_PLAIN, 3, [1 - v for v in self.color], 5)

    @staticmethod
    def find(image, offs_x=0, offs_y=0, ppm_x=1, ppm_y=1):
        if not settings.on_pi:
            grad_val = max(cv2.getTrackbarPos('grad_val', 'beamer'), 1)
            acc_thr = max(cv2.getTrackbarPos('acc_thr', 'beamer'), 1)
            dp = max(cv2.getTrackbarPos('dp', 'beamer'), 1)
            min_dist = max(cv2.getTrackbarPos('min_dist', 'beamer'), 1)
            min_radius = cv2.getTrackbarPos('min_radius', 'beamer')
            max_radius = cv2.getTrackbarPos('max_radius', 'beamer')
        else:
            grad_val = Ball.grad_val
            acc_thr = Ball.acc_thr
            dp = Ball.dp
            min_dist = Ball.min_dist
            min_radius = Ball.min_radius
            max_radius = Ball.max_radius
        # create gray image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # gray = cv2.medianBlur(gray, 5)
        # find circles in image
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=dp, minDist=min_dist, param1=grad_val,
                                   param2=acc_thr, minRadius=min_radius, maxRadius=max_radius)
        # found circles with position in pixels relative from image origin in upper left corner
        balls = []
        if circles is not None:
            for circle in circles[0, :]:
                # get relative position from image origin, convert to mm and subtract camera offset
                balls.append(Ball(circle[0] / ppm_x + offs_x, circle[1] / ppm_y + offs_y))
                # if settings.debug:
                #    print("ball found: {} (mm)".format(balls[len(balls)-1]))
        if len(balls) == 0:
            balls = None
        return balls

    def __str__(self):
        return 'x:{} y:{} value:{}'.format(self.x, self.y, ball_value(self.color))
