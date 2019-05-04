""" imports """


class InputStream:

    def __init__(self):
        """
        Open (first available or specified) input as video capture and initialize queue
        """
        pass

    def update(self):
        """
        Threaded input read, adds frame to queue
        """
        # threaded:
        # read from VideoCapture and add to frame queue
        pass

    def read(self):
        """
        Get frame from input queue
        :returns: the first frame in the input queue
        """
        pass
