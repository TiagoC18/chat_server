"""Protocol for chat server - Computação Distribuida Assignment 1."""
import json
from datetime import datetime
from socket import socket


class Message:
    """Message Type."""
    def __init__(self, command):
        """Initialize message."""
        self.command = command
        self.timestamp = int(datetime.now().timestamp())
        

    
class JoinMessage(Message):
    """Message to join a chat channel."""
    def __init__(self, channel, command):
        """Initialize join message."""
        super().__init__(command)
        self.channel = channel
    def __str__(self):
        """String representation of message."""
        return f'{{"command": "{self.command}", "channel": "{self.channel}"}}'


class RegisterMessage(Message):
    """Message to register username in the server."""
    def __init__(self, name, command):
        """Initialize register message."""
        super().__init__(command)
        self.name = name
    def __str__(self):
        """String representation of message."""
        return f'{{"command": "{self.command}", "user": "{self.name}"}}'

    
class TextMessage(Message):
    """Message to chat with other clients."""
    def __init__(self, message, channel, command):
        """Initialize text message."""
        super().__init__(command)
        self.message = message
        self.channel = channel
    def __str__(self):
        """String representation of message."""
        if self.channel == None:
            return f'{{"command": "{self.command}", "message": "{self.message}", "ts": {int(datetime.now().timestamp())}}}'
        else:
            return f'{{"command": "{self.command}", "message": "{self.message}", "channel": "{self.channel}", "ts": {self.timestamp}}}'


class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, username: str) -> RegisterMessage:
        """Creates a RegisterMessage object."""
        return RegisterMessage(username, "register")

    @classmethod
    def join(cls, channel: str) -> JoinMessage:
        """Creates a JoinMessage object."""
        return JoinMessage(channel, "join")
    @classmethod
    def message(cls, message: str, channel: str = None) -> TextMessage:
        """Creates a TextMessage object."""
        return TextMessage(message, channel, "message")

    @classmethod
    def send_msg(cls, connection: socket, msg: Message):
        """Sends through a connection a Message object."""
        if (msg.command == "register"):
            jsondata = json.dumps({"command": msg.command, "user": msg.name}).encode('utf-8')
        elif (msg.command == "join"):
            jsondata = json.dumps({"command": msg.command, "channel": msg.channel}).encode('utf-8')
        elif (msg.command == "message"):
            if msg.channel == None:
                jsondata = json.dumps({"command": msg.command, "message": msg.message, "ts":int(datetime.now().timestamp())}).encode('utf-8')
            else:   
                jsondata = json.dumps({"command": msg.command, "message": msg.message, "channel": msg.channel, "ts":int(datetime.now().timestamp())}).encode('utf-8')

        connection.send(len(jsondata).to_bytes(2, 'big')+jsondata)


    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""
        bytesIniciais = connection.recv(2)
        if not bytesIniciais:
            return None
        
        cabecalho = int.from_bytes(bytesIniciais, 'big')
        data = connection.recv(cabecalho).decode('utf-8')

        try:
            comando = json.loads(data)["command"]
        except:
            raise CDProtoBadFormat()

        if comando == "register":
                return CDProto.register(json.loads(data)["user"])
        elif comando == "join":
                return CDProto.join(json.loads(data)["channel"])
        elif comando == "message":
            if "channel" in json.loads(data):
                return CDProto.message(json.loads(data)["message"], json.loads(data)["channel"])
            else:
                return CDProto.message(json.loads(data)["message"])
       
       


class CDProtoBadFormat(Exception):
    """Exception when source message is not CDProto."""

    def __init__(self, original_msg: bytes=None) :
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode('')
    