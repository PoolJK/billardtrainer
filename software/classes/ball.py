""" imports """


class Ball:

    """
    A ball on the snooker table. Holds position, colour, detection values and methods
    """
    radius = 26.25  # [mm]

    def __init__(self, position, colour):
        """
        Generate new ball
        :param position: position of center in [mm] (table coordinate system)
        :param colour: ball colour
        """
        self.position = position
        self.colour = colour

    @staticmethod
    def find(image):
        # find balls on the image and return them in a list
        pass
