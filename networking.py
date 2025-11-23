import socket
import threading
import time 
import select
from queue import Queue 



class Response:
    '''
    this class takes in a message received from a client
    and parses it into veriables with | as a delimiter
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
            self.data = {'TTD': message[1], 'DTS': message[2], 'motor_data': message[3]}
            
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
        Continuously accept connections. After a client disconnects the loop
        continues so the server keeps listening for new connections.
        '''
        while not self.shutdown:
            try:
                self.client, self.client_addr = soc.accept()
            except Exception:
                # if socket was closed or interrupted, exit
                break
            print('connection accepted from:', self.client_addr)
            self.has_client = True

            # monitor the client for disconnection without consuming data
            try:
                while not self.shutdown and self.client is not None:
                    # use select to check if socket is readable
                    r, _, _ = select.select([self.client], [], [], 1.0)
                    if r:
                        try:
                            # peek to see if connection closed (0 bytes means closed)
                            data = self.client.recv(1, socket.MSG_PEEK)
                            if not data:
                                break
                        except BlockingIOError:
                            # no data available yet
                            continue
                        except Exception:
                            # any error -> treat as disconnect
                            break
                    # otherwise timeout — loop again to check shutdown
            finally:
                print('client disconnected:', self.client_addr)
                try:
                    if self.client is not None:
                        self.client.close()
                except Exception:
                    pass
                self.client = None
                self.client_addr = None
                self.has_client = False


    def destroy(self):
        print('deconstructing')
        self.shutdown = True
        if self.client is not None:
            self.client.close()
        try:
            self.sock.close()
        except Exception:
            pass

    def recieve_message(self):
        '''
        gets message in form: type|
        returns response type
        '''
        if not self.has_client or self.client is None:
            raise RuntimeError("No client connected")
        try:
            message_bytes = self.client.recv(128)
            if not message_bytes:
                # remote closed
                self.has_client = False
                try:
                    self.client.close()
                except Exception:
                    pass
                self.client = None
                raise RuntimeError("Client disconnected")
            message = self.__decode(message_bytes)
            return Response(message, self.client_addr)
        except Exception:
            # propagate as runtime error so callers can handle reconnect
            raise

    def send_message(self, rqst: Request):
        message = rqst.request_type + '|' + rqst.mode_requsted
        if not self.has_client or self.client is None:
            raise RuntimeError("No client connected")
        try:
            self.client.send(self.__encode(message))
        except Exception:
            # mark client as gone so accept loop can continue
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None
            self.has_client = False
            raise

    def __encode(self, message):
        return message.encode()
    
    def __decode(self, message_bytes):
        return message_bytes.decode()
