import socket as s
from select import select
from queue import Queue as queue, Empty as empty

sock = s.socket(s.AF_INET, s.SOCK_STREAM)
sock.setblocking(0)

addr = (s.gethostbyname(s.gethostname()), 666)
print('hosting on {}:{}'.format(*addr))
sock.bind(addr)

sock.listen(5)

INPUT = [sock]
OUTPUT = []

message_queues = {}

while INPUT:
    read, write, exce = select(INPUT, OUTPUT, INPUT)
    
    if len(read):
        print('<SERVER EVENT> checking inputs')
    for socket in read:
        if socket == sock:
            client, address = socket.accept()
            INPUT.append(client)
            
            print(f'<CONNECTION EVENT> new connection from {address[0]} ({address[1]})')
            message_queues[client] = queue()
        
        else:
            data = socket.recv(2048)
            if not data:

                address = socket.getpeername()
                print(f'<CONNECTION EVENT> closed connection from {address[0]} ({address[1]}) reason: empty message received')

                if socket in OUTPUT:
                    OUTPUT.remove(socket)
                INPUT.remove(socket)
                del message_queues[socket]
                socket.close()
            
            else:

                address = socket.getpeername()
                print(f'<MESSAGE EVENT> received {data} from {address[0]} ({address[1]})')

                for client in INPUT:
                    if client == socket or client == sock:
                        continue
                    if not (client in OUTPUT):
                        OUTPUT.append(client)
                    message_queues[client].put(data)
    if len(write):
        print('<SERVER EVENT> checking outputs')
    for socket in write:
        address = socket.getpeername()
        try:
            data = message_queues[socket].get_nowait()
            socket.send(data)
            print(f'<MESSAGE EVENT> sent {data} to {address[0]} ({address[1]})')
        except empty as e:
            print(f'<MESSAGE EVENT> removed {address[0]} ({address[1]}) from outputs')
            OUTPUT.remove(socket)

    for socket in exce:
        address = socket.getpeername()
        print(f'<CONNECTION ERROR> closed connection from {address[0]} ({address[1]}) reason: brutally disconnected')

        if socket in OUTPUT:
            OUTPUT.remove(socket)
        INPUT.remove(socket)
        del message_queues[socket]
        socket.close()
