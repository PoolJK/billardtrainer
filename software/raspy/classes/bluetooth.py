""" imports """


class Bluetooth:

    message_queue = None

    def __init__(self):
        """
        Bluetooth class holding in/out message queue, connection and send/receive methods
        """
        # if not load_configuration:
        #   create defaults
        #   start_pairing()
        # else:
        #   if connect():
        #       start exchange thread(s)
        pass

    def start_pairing(self):
        """
        Initiate first connection to device running billardtrainer app
        :return: 1 on success, 0 on failure
        """
        # set visible
        # wait for connection
        # accept pairing
        # save configuration
        # if paired:
        #   return 1
        pass

    def connect(self):
        # open connection
        # if connected return 1
        # start Thread adding messages and data to queue
        pass

    def read(self):
        # return first message from queue (or None)
        pass

    def send(self, data):
        # add data to send queue
        pass
