import socket
import threading
import time 
from queue import Queue 



class inMessage:
    def __init__(self, data: str, clientAddr):
        self.data = data
        self.clientAddr = clientAddr

class outMessage: 
    def __init__(self, data: str):
        self.data = data

