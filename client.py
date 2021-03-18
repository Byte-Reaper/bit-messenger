import socket as s
from select import select
from cryptography.fernet import Fernet, InvalidToken

sock = s.socket(s.AF_INET, s.SOCK_STREAM)
sock.setblocking(0)
sock.settimeout(1)

addr = input('server address:         ')
port = int(input('server port:            '))
uname= input('who are you:            ')
hostmode = input('are you the host?: [y/n]').lower() in ['y', '', 'yes', 'ye']

#sock.connect((addr, port))
if hostmode:
    key = Fernet.generate_key()
    print(f'this is your key: {key} send this to the members of your chat session')

else:
    key = bytes(input('key:                    '), 'utf-8')

fernet = Fernet(key)

sock = s.socket(s.AF_INET, s.SOCK_STREAM)

sock.connect((addr, port))

import  threading

running = True

def send():
    while running:
        msg = input()
        if msg:
            sock.send(fernet.encrypt(f'<{uname}> {msg}'.encode('utf-8')))

t = threading.Thread(target=send)
t.start()
while True:
    r, w, _ = select([sock], [sock], [sock], 1)
    for client in r:
        try:
            data = fernet.decrypt(client.recv(2048)).decode('utf-8')
            print(data)
        except InvalidToken:
            pass