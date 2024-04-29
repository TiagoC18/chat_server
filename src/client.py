"""CD Chat client program"""
import logging
import sys
import socket
import selectors
import fcntl
import os

from .protocol import CDProto, CDProtoBadFormat

logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG)

class Client:
    """Chat Client process."""

    def __init__(self, name: str = "Foo"):
        """Initializes chat client."""
        self.name = name
        self.channel = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.selector = selectors.DefaultSelector()

    def connect(self):
        """Connect to chat server and setup stdin flags."""
        self.socket.connect(('localhost', 5000))
        self.selector.register(self.socket, selectors.EVENT_READ, self.read)
        self.send_registration()

    def send_registration(self):
        """Send registration to the server."""
        msg = CDProto.register(self.name)
        CDProto.send_msg(self.socket, msg)

    def read(self, socket, mask):
        """Handle messages received from the server."""
        msg = CDProto.recv_msg(self.socket)
        logging.debug('Received: %s', msg)
        if msg.command == "message":
            print(f"{msg.channel} -> {msg.message}")
        elif msg.command == "join":
            print(f"Joined channel {msg.channel}")
        elif msg.command == "register":
            print(f"Registered as {msg.name}")

    def read_keyboard_input(self, stdin, mask):
        """Handle keyboard input."""
        input = sys.stdin.readline()
        if input.startswith("/join"):
            msg = CDProto.join(input[6:-1])
            CDProto.send_msg(self.socket, msg)
            self.channel = msg.channel
        elif input == "exit\n":
            self.socket.close()
            sys.exit("Exiting chat client.")
        else:
            msg = CDProto.message(input[:-1], self.channel)
            CDProto.send_msg(self.socket, msg)


    def loop(self):
        """Loop indefinetely."""
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)
        self.selector.register(sys.stdin, selectors.EVENT_READ, self.read_keyboard_input)
        while True:
            sys.stdout.write('Type something and hit enter: ')
            sys.stdout.flush()
            for k, mask in self.selector.select():
                callback = k.data
                callback(k.fileobj,mask)


