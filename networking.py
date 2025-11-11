import socket
import threading
import time 
from queue import Queue 



class Response:
    '''
    
    '''
    def __init__(self, msg: str, clientAddr):
        message = msg.split('|')
        if message[0] == 'update':
            self.type = 'update'
            self.mode = message[1]
            self.battery = message[2]
        elif message[0] == 'alert':
            self.type = 'alert'
            self.mode = 'search'
        elif message[0] == 'log':
            self.type = 'log'
            self.mode = 'transmit'
            self.data = {'TTD': message[1], 'DTS': message[2], 'Name': message[3]}
            
        self.clientAddr = clientAddr

class Request: 
    '''
    of form: request_type|mode_requested
    '''
    def __init__(self, request_type: str, mode_requsted: str = ''):
        '''
        request_type: update or contol
        mode_requsted: string representing mode requested
        '''
        '''
        match mode_requsted:
            case 'standby':
                self.mode_requsted = '0'
            case 'search':
                self.mode_requsted = '1'
            case 'transmit':
                self.mode_requsted = '2'
            case 'RTB':
                self.mode_requsted = '3'
            case _:
                self.mode_requsted = ''  # invalid mode or none provided
        '''
        self.request_type = request_type
        self.mode_requsted = mode_requsted

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
        self.sock.listen(1)
        print('listening for connection on port:', port)
        connector = threading.Thread(target=self.__wait_for_connection_thread, daemon=True, args=[self.sock])
        connector.start()

    def __wait_for_connection_thread(self, soc: socket.socket) -> None:
        '''
        Establish a connection with a client, and die
        '''
        self.client, self.client_addr = soc.accept()
        print('connection accepted from:', self.client_addr)
        self.has_client = True


    def destroy(self):
        print('deconstructing')
        self.shutdown = True
        if self.client is not None:
            self.client.close()

    def recieve_message(self):
        '''
        gets message in form: type|
        returns response type
        '''
        message_bytes = self.client.recv(128)
        message = self.__decode(message_bytes)
        return Response(message, self.client_addr)

    def send_message(self, rqst: Request):
        message = rqst.request_type + '|' + rqst.mode_requsted
        self.client.send(self.__encode(message))

    def __encode(self, message):
        return message.encode()
    
    def __decode(self, message_bytes):
        return message_bytes.decode()
