import networking as nt

server = nt.WiFiChannel()
server.accept_connection()
while not server.shutdown:
    msg = server.recieve_message()
    if msg == 'close':
        server.destroy()
        server.shutdown = True
        continue
    elif msg == 'port':
        server.send_message(str(server.port))
    print('listening for new message')

print('goodbye')
