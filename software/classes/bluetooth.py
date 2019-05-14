from bluetooth import *
from threading import Thread
from queue import Queue


class BT:

    def __init__(self):
        self.server = self.init_server()
        self.client = self.get_client_connection(self.server)
        self.message_queue = Queue(10)
        self.bt = Thread(target=self.manage_connection(self.client))
        print("terminating...")

    def read(self):
        ret = self.message_queue.get(timeout=5)
        return ret

    def send(self, data):
        self.client.send("Echo from Pi: [%s]\n" % data)

    @staticmethod
    def init_server():
        server_sock = BluetoothSocket(RFCOMM)
        server_sock.bind(("", PORT_ANY))
        server_sock.listen(1)
        uuid = "00001101-0000-1000-8000-00805F9B34FB"
        try:
            advertise_service(server_sock, "Echo Server",
                              service_id=uuid,
                              service_classes=[uuid, SERIAL_PORT_CLASS],
                              profiles=[SERIAL_PORT_PROFILE]
                              )
        except Exception as e:
            print(e)
        return server_sock

    @staticmethod
    def get_client_connection(server_sock):
        print("Waiting for connection")
        client_sock, client_info = server_sock.accept()
        print("accepted connection from ", client_info[0])
        return client_sock

    def manage_connection(self, _socket):
        try:
            data = _socket.recv(1024)
            while True:
                print("received [%s]" % data)
                self.message_queue.put(data)
                self.send(self.read())
                data = _socket.recv(1024)
        except IOError:
            pass
        self.client.close()
        self.server.close()
