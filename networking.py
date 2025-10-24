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

class WiFiChannal:
    '''
    set up connection
    send and receive messages
    '''
    def __init__(self, port: int=5000):
        #signal to start shut down 
        self.shutdown = False
        self.has_client = False

        #client obj and its address
        self.client = None
        self.client_addr = None

        #socket creation and set up
        # Socket creation
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # $ sudo iptables -I INPUT -s ESP.IP.GOES.HERE -p tcp --dport 15000 -j ACCEPT 
        sock.bind(('0.0.0.0', port))
        sock.listen(0)


    def destroy(self):
        print('deconstructing')
        self.shutdown = True
        if self.client is not None:
            self.client.close()

    def receive_message(self):
        message_bytes = self.client.recv(128)
        message = self.__decode(message_bytes)
        return message

    def send_message(self, message):
        self.client.send(self.__encode(message))

    def __encode(self, message):
        return message.data.encode()
    
    def __decode(self, message_bytes):
        return message_bytes.decode()
