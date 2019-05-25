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

    TODO: move to readme
    add pi to bluetooth group:
    sudo usermod -G bluetooth -a pi
    check:
    cat /etc/group | grep bluetooth
    change group of sdp:
    sudo chgrp bluetooth /var/run/sdp
    """

    def __init__(self):
        self.server = None
        self.client = None
        self.message_queue = Queue(100)
        self.send_queue = Queue(1000)
        self.bt = Thread(target=self.manage_connection, args=())
        self.bt.daemon = True
        self.bt.start()
        self.send_thread = Thread(target=self.flush_send_queue, args=())
        self.send_thread.daemon = True

    def read(self):
        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None

    def send(self, data):
        self.send_queue.put(data)
        if not self.send_thread.is_alive():
            self.send_thread = Thread(target=self.flush_send_queue, args=())
            self.send_thread.daemon = True
            self.send_thread.start()

    # https://stackoverflow.com/questions/34599703/rfcomm-bluetooth-permission-denied-error-raspberry-pi
    # https://github.com/ev3dev/ev3dev/issues/274
    @staticmethod
    def init_server():
        try:
            server_sock = BluetoothSocket(RFCOMM)
            server_sock.bind(("", PORT_ANY))
            server_sock.listen(1)
            uuid = "00001101-0000-1000-8000-00805F9B34FB"
            advertise_service(server_sock, "Echo Server",
                              service_id=uuid,
                              service_classes=[uuid, SERIAL_PORT_CLASS],
                              profiles=[SERIAL_PORT_PROFILE]
                              )
        except OSError:
            # so far this happens when there is no bluetooth hardware present, so just exit the thread
            wait(1000)
            print('init_server: bluetooth error, exiting thread:')
            traceback.print_exc()
            exit(0)
        else:
            return server_sock

    @staticmethod
    def get_client_connection(server_sock):
        print("Waiting for connection")
        client_sock, client_info = server_sock.accept()
        print("accepted connection from ", client_info[0])
        return client_sock

    def manage_connection(self):
        # TODO: https://stackoverflow.com/questions/8386679/why-am-i-receiving-a-
        #  string-from-the-socket-until-the-n-newline-escape-sequence
        connection_attempts = 0
        while True:
            connection_attempts += 1
            self.server = self.init_server()
            self.client = self.get_client_connection(self.server)
            try:
                data = self.client.recv(1024)
                if data == 'b\'exit\'':
                    break
                while True:
                    # print("bluetooth.py: received \"{}\"".format(data))
                    data = str(data).lstrip('b').strip('\'')
                    data = data.split('\\n')
                    for line in data:
                        if line != '':
                            self.message_queue.put(line)
                            # self.send('size={}'.format(len(line)))
                    data = self.client.recv(1024)
            except IOError as e:
                print('connection lost', e)
            self.client.close()
            self.server.close()
        print("terminating...")
        self.client.close()
        self.client = None
        self.server.close()

    def flush_send_queue(self):
        while not self.send_queue.empty():
            data = self.send_queue.get_nowait()
            while self.client is None:
                print('send_queue: client is None. Qsize: {}'.format(self.send_queue.qsize() + 1))
                wait(5000)
            self.client.send("%s\n" % data)
