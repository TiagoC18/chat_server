"""CD Chat server program."""
import logging
import socket
import selectors
from .protocol import CDProto, CDProtoBadFormat

logging.basicConfig(filename="server.log", level=logging.DEBUG)

class Server:
    """Chat Server process."""
    def __init__(self, address='localhost', port=5000):
        self.address = address
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.address, self.port))
        self.server_socket.listen(100)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.server_socket, selectors.EVENT_READ, self.accept)
        self.client_channels = {}  

    def accept(self, server_socket, mask):
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        self.selector.register(client_socket, selectors.EVENT_READ, self.read)
        self.client_channels[client_socket] = [None]  # no channel yet

    def read(self, client_socket, mask):
        message = CDProto.recv_msg(client_socket)
        if not message is None:
            logging.debug('Received: %s', message)
            self.process_message(client_socket, message)

        else:
            self.close_connection(client_socket)

    def process_message(self, client_socket, message):
        if message.command == "register":
            #self.client_channels[client_socket] = [None]  # re-registration
            CDProto.send_msg(client_socket, message)
        elif message.command == "join":
            if self.client_channels[client_socket]==None:
                self.client_channels[client_socket].remove(None)
            if message.channel not in self.client_channels[client_socket]:
                self.client_channels[client_socket].append(message.channel)
            CDProto.send_msg(client_socket, message)
        elif message.command == "message":
            self.broadcast_message(message)

    def broadcast_message(self, message):
        for client, channels in self.client_channels.items():
            if message.channel in channels:
                CDProto.send_msg(client, message)

    def close_connection(self, client_socket):
        logging.info("Closing connection")
        self.selector.unregister(client_socket)
        client_socket.close()
        self.client_channels.pop(client_socket, None)

    def loop(self):
        """Loop indefinetely."""
        print(f"Server running on {self.address}:{self.port}")
        while True:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

