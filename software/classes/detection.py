""" imports """
# from .camera import Camera


class Detection:

    # message or message_queue = None
    # data or data_queue = None

    def __init__(self, camera):
        """
        Class holding the detection algorithm(s) and an event queue to be read by the main loop
        :param camera: used as input device
        :returns: 1 if configuration loaded successfully, 0 if not
        """
        # if load_last_configuration:
        #   return 1
        # else:
        #   create defaults
        #   return 0
        pass

    def start(self):
        """
        Start a threaded detection reading from input device, analyzing and adding to event queue
        """
        # start live detection and analysis in separate thread
        # set self.message and self.data or add to their queues
        pass

    def read(self):
        """
        Get the next event from the queue
        :returns: the first (message, data)-pair from the event queue or (None, None)
        """
        # return (current) message or first message in queue, (current) data or first data in queue
        pass
