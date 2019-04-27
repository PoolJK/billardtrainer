""" imports """
# from .classes import camera, beamer, bluetooth, detection


""" argparse """
# argparse (during development)


""" main """


def main():
    # if not camera.init or not beamer.init:
    #   calibrate(camera, beamer)
    # bluetooth.init
    # detection.init(camera)
    # while True:
    #   process bluetooth data:
    #   message, data = bluetooth.read
    #   if message is not None:
    #       if message == send_data:
    #           send_data()
    #       elif message == show:
    #           show(data)
    #       .
    #       .
    #       .
    #       continue
    #   process detection data
    #   message, data = detection.read
    #   if message is not None:
    #       do something according to analysis in detection (send data or signal)
    #
    #   if some_exit_condition (shutdown?):
    #       break
    pass


""" methods """


def calibrate(camera, beamer):
    # perform some magic:
    # if not camera.is_calibrated:
    #   calibrate for camera distortion
    # if not beamer.is_calibrated:
    #   calibrate for camera / beamer displacement
    # calibrate for placement above table
    pass


def send_data(data):
    # data examples
    # ball_coordinates=None, colours=None, speeds=None, etc=None
    # bluetooth.send(data)
    pass


def send_signal(signal):
    # signal example:
    # movement_detected=None, all_balls_at_rest=None, no_lights=None, etc=None
    # bluetooth.send(signal)
    pass


def show(data):
    # beamer.show(data)
    pass


main()
