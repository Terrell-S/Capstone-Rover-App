import socket
import threading
import time 
from queue import Queue 



class Response:
    '''
    
    '''
    def __init__(self, data: str, clientAddr):
        self.data = data
        self.clientAddr = clientAddr

class Request: 
    def __init__(self, data: str):
        self.data = data

class WiFiChannel:
    '''
    set up connection
    send and receive messages
    '''
    def __init__(self, port: int=5000):
        self.port = port
        #signal to start shut down 
        self.shutdown = False
        self.has_client = False

        #client obj and its address
        self.client = None
        self.client_addr = None

        #socket creation and set up
        # Socket creation
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # $ sudo iptables -I INPUT -s ESP.IP.GOES.HERE -p tcp --dport 15000 -j ACCEPT 
        self.sock.bind(('0.0.0.0', port))
        self.sock.listen(0)
        print('listening for connection on port:', port)

    def accept_connection(self):
        self.client, self.client_addr = self.sock.accept()
        print('connection accepted from:', self.client_addr)
        self.has_client = True


    def destroy(self):
        print('deconstructing')
        self.shutdown = True
        if self.client is not None:
            self.client.close()

    def recieve_message(self):
        message_bytes = self.client.recv(128)
        message = self.__decode(message_bytes)
        print('message recieved:', message)
        return message

    def send_message(self, message):
        self.client.send(self.__encode(message))

    def __encode(self, message):
        return message.encode()
    
    def __decode(self, message_bytes):
        return message_bytes.decode()
