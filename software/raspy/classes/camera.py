"""" imports """


class Camera:

    is_calibrated = False
    calibration = None

    def __init__(self):
        """
        Camera class holding calibration data (scale, offset, undistortion)
        :returns: 1 if configuration loaded successfully, 0 if not
        """
        # if load from file:
        #   is_calibrated = True
        #   return 1
        # else:
        #   create defaults
        #   return 0
        pass

    def get_frame(self):
        """
        Read (the next) frame from the input stream
        :returns: the grabbed frame
        """
        # read frame from inputstream
        # if is_calibrated:
        #   undistort frame
        # return frame
        pass

    def undistort(self, frame):
        """
        Undistort the input image with the given calibration data
        :param frame: the image to undistort
        :returns: the undistorted image
        """
        # apply calibration
        # return undistorted frame
        pass
