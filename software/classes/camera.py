"""" imports """


class Camera:

    is_calibrated = False
    calibration = None

    def __init__(self):
        # if load from file:
        #   is_calibrated = True
        #   return 1
        # else:
        #   create defaults
        #   return 0
        pass

    def get_frame(self):
        # read frame from inputstream
        # if is_calibrated:
        #   undistort frame
        # return frame
        pass

    def undistort(self, frame):
        # apply calibration
        # return undistorted frame
        pass
