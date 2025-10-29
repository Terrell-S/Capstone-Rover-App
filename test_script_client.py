import networking as nt
import socket

sock = socket.socket()
sock.connect(('127.0.0.1',5000 ))

msg = ''
while msg != 'close':
    msg = input("enter message: ")
    sock.send(msg.encode())
    if msg == 'port':
        port_bytes = sock.recv(128)
        port = port_bytes.decode()
        print('server port is:', port)

print('goodbye')



