""" imports """


class Bluetooth:

    message_queue = None

    def __init__(self):
        # if not load_configuration:
        #   create defaults
        #   start_pairing()
        # else:
        #   if connect():
        #       start exchange thread(s)
        pass

    def start_pairing(self):
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
