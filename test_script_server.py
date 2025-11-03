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
    message = msg.split('|')
    if message[0] == 'update':
        print('mode is now: ', message[1])
        print('TOA is now: ', message[2])
        print('DTS is now: ', message[3])
    print('listening for new message')

print('goodbye')
