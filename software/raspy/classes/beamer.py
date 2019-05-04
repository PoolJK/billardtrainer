""" imports """


class Beamer:

    is_calibrated = False

    def __init__(self):
        """
        Beamer class holding calibration data (scale, offset, distortion correction)
        and methods to display images or data on the table
        :returns: 1 if configuration loaded successfully, 0 if not
        """
        # if load from file:
        #   self.is_calibrated = True
        #   return 1
        # else:
        #   create defaults
        #   return 0
        pass

    def show(self, image=None, data=None):
        """
        Update the beamer image on the table
        :param image: an image to show on the beamer
        :param data: items to show (text, ball outlines, areas etc)
        """
        # if image is None and data is None:
        #   clear output
        # apply calibration to image or data
        # show image or data
        pass
