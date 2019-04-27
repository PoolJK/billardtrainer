""" imports """


class Ball:

    radius = 26.25  # [mm]

    def __init__(self, position, colour):
        """
        A ball on the snooker table. Holds position, colour, detection values and methods
        :param position: position of center in [mm] (table coordinate system)
        :param colour: ball colour
        """
        self.position = position
        self.colour = colour

    @staticmethod
    def find(image):
        """
        Find all balls in the specified image and return them in a list
        :param image: the image to be searched
        :returns: list<Ball>
        """
        # find balls on the image and return them in a list
        pass
