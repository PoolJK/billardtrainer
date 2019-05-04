""" imports """
# from .classes import camera, beamer, bluetooth, detection


""" argparse """
# argparse (during development)


""" main """


def main():
    """
    The main loop. Initializes system parts on start, then runs through detection and bluetooth loops
    """
    # if not camera.is_calibrated or not beamer.is_calibrated:
    #   calibrate(camera, beamer)
    #
    # bluetooth.init
    # detection.init(camera)
    #
    # while True:
    #
    #   process bluetooth data:
    #   message, data = bluetooth.read
    #   if message is not None:
    #       if message == send_data:
    #           send_data()
    #       elif message == show:
    #           beamer.show(data)
    #       .
    #       .
    #       .
    #       continue
    #
    #   process detection data
    #   message, data = detection.read
    #   if message is not None:
    #       do something according to analysis in detection (send data or signal)
    #       if message == no_movement:
    #       elif message == no_balls_detected
    #       .
    #       .
    #       .
    #       continue
    #
    #   if some_exit_condition (shutdown?):
    #       break
    pass


""" methods """


def calibrate(camera, beamer):
    """
    Perform some OpenCV magic here
    :param camera: the systems camera
    :param beamer: the systems beamer
    """
    # perform some magic:
    # if not camera.is_calibrated:
    #   calibrate for camera distortion
    # if not beamer.is_calibrated:
    #   calibrate for camera / beamer displacement
    # calibrate for placement above table
    pass


# just do it
main()
