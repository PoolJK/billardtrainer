import cv2
from software.raspy.settings import Settings


class Ball:
    """
    Parameters and functions for ball
    """

    def __init__(self, x, y, radius, color=None):
        """
        Generate new ball
        :param x: x-position of center in mm
        :param y: y-position of center in mm
        :param radius: radius in mm
        :param color: ball color
        """
        if color is None:
            color = [33, 55, 77]
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw_self(self, outpict, pixel_per_mm=None, offset_x=None, offset_y=None):
        # draw mid point for debugging
        if Settings.debugging:
            cv2.drawMarker(outpict, (int((self.x + offset_x) * pixel_per_mm), int((self.y + offset_y) / pixel_per_mm)),
                           (0, 0, 255), cv2.MARKER_CROSS, int(self.radius / 2 * pixel_per_mm), 1)
        # circle outline
        cv2.circle(outpict, (int((self.x + offset_x) * pixel_per_mm), int((self.y + offset_y) * pixel_per_mm)),
                   int(self.radius) + 5, (255, 255, 255), 3)

    @staticmethod
    def find_self(image, pix_per_mm):
        """
        Find balls in image
        :param image: Image for houghCircles algorithm
        :param pix_per_mm: pixel per mm value to save balls as mm coordinates
        :return: list with found balls
        """

        # HoughCircles parameters
        p1 = 50
        p2 = 29
        min_radius = 16
        max_radius = 28

        # create gray image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        rows = gray.shape[0]
        # print("{} {} {} {}".format(p1, p2, min_radius, max_radius))

        # find circles in image
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=p1,
                                   param2=p2, minRadius=min_radius, maxRadius=max_radius)

        balls = []

        if circles is not None:
            for i in circles[0, :]:
                # balls.append(Ball(i[0], i[1], i[2]))
                balls.append(Ball(i[0] / pix_per_mm, i[1] / pix_per_mm, i[2] / pix_per_mm))

        return balls
