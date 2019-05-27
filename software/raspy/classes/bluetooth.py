import traceback

from bluetooth import *
from threading import Thread
from queue import Queue
import queue

from .utils import *


class BT:
    """
    Class for bluetooth hardware handling.
    Provides read() and send() with queues
    """

    def __init__(self):
        self.server = None
        self.client = None
        self.message_queue = Queue(100)
        self.send_queue = Queue(10)
        self.bt = Thread(target=self.manage_connection, args=())
        self.bt.daemon = True
        self.bt.start()
        self.send_thread = Thread(target=self.flush_send_queue, args=())
        self.send_thread.daemon = True
        self.exit_requested = False

    def read(self):
        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None

    def read_blocking(self):
        try:
            return self.message_queue.get(timeout=1)
        except queue.Empty:
            debug('bluetooth: bt_queue empty after 5s')
            return None

    def send(self, data):
        try:
            self.send_queue.put_nowait(data)
        except queue.Full:
            self.send_queue.get_nowait()
            self.send_queue.put_nowait(data)
        if not self.send_thread.is_alive():
            self.send_thread = Thread(target=self.flush_send_queue, args=())
            self.send_thread.daemon = True
            self.send_thread.start()

    def manage_connection(self):
        """
        The main bluetooth loop. Creates a socket and starts listening in a loop, exiting on failure.
        After running through, does nothing
        """
        connection_attempts = 0
        while True:
            connection_attempts += 1
            # https://stackoverflow.com/questions/34599703/rfcomm-bluetooth-permission-denied-error-raspberry-pi
            # https://github.com/ev3dev/ev3dev/issues/274
            # create new server socket
            try:
                self.server = BluetoothSocket(RFCOMM)
                self.server.bind(("", PORT_ANY))
                self.server.listen(1)
                uuid = "00001101-0000-1000-8000-00805F9B34FB"
                advertise_service(self.server, "Echo Server",
                                  service_id=uuid,
                                  service_classes=[uuid, SERIAL_PORT_CLASS],
                                  profiles=[SERIAL_PORT_PROFILE]
                                  )
            except OSError:
                # so far this happens when there is no bluetooth hardware present, so just exit the thread
                wait(1000)
                traceback.print_exc()
                wait(500)
                print('seems like u got no colored teeth')
                exit(0)
            print("Waiting for connection")
            self.client, client_info = self.server.accept()
            print("accepted connection from ", client_info[0])
            try:
                # initial read
                data = self.client.recv(1024)
                # receiving loop:
                while True:
                    debug("bluetooth.py: received \"{}\"".format(data), 0)
                    data = str(data).lstrip('b').strip('\'')
                    # split message in case two lines are received at once
                    data = data.split('\\x04')
                    for line in data:
                        if line != '':
                            line = line.strip(chr(4)).strip('\\x04')
                            self.message_queue.put(line)
                            debug('bluetooth: queued line: \"{}\"'.format(line), 0)
                    data = self.client.recv(1024)
            except IOError as e:
                print('connection lost', e)
            self.client.close()
            self.server.close()
            if self.exit_requested:
                break
        print("terminating...")
        self.client.close()
        self.client = None
        self.server.close()

    def flush_send_queue(self):
        while not self.send_queue.empty():
            data = self.send_queue.get_nowait()
            while self.client is None:
                print('send_queue: not connected, sleeping 1s. Q.size: {}'.format(self.send_queue.qsize() + 1))
                wait(1000)
            self.client.send("%s\n" % data)
