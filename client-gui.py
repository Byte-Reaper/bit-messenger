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
    print(f"this is your key: '{str(key)[2:-1]}' send this to the members of your chat session")

else:
    key = bytes(input('key:                    '), 'utf-8')

fernet = Fernet(key)

sock = s.socket(s.AF_INET, s.SOCK_STREAM)

sock.connect((addr, port))

import tkinter, tkinter.scrolledtext

running = True

window = tkinter.Tk(className="Bit messenger client")

def send():
    global hist
    msg = message_box.get()
    message_box.delete(0, tkinter.END)
    if msg:
        msg = f'<{uname}> {msg}'
        hist += msg + '\n'
        edit_history(hist)
        sock.send(fernet.encrypt(msg.encode('utf-8')))

history = tkinter.scrolledtext.ScrolledText(window, width=100, height=30, state=tkinter.DISABLED, wrap=tkinter.WORD)
history.grid(row=0, column=0, columnspan=10)
hist = ''
message_box = tkinter.Entry(window, width=130)
message_box.grid(row=10, column=0, columnspan=9)
send_button = tkinter.Button(window, text="SEND", command=send)
send_button.grid(row=10, column=9)

def edit_history(new):
    history.configure(stat=tkinter.NORMAL)
    history.delete(1.0, tkinter.END)
    history.insert(tkinter.INSERT, new)
    history.configure(stat=tkinter.DISABLED)

while True:
    r, w, _ = select([sock], [sock], [sock], 1)
    for client in r:
        try:
            data = fernet.decrypt(client.recv(2048)).decode('utf-8')
            hist += data + '\n'
            edit_history(hist)
        except InvalidToken:
            pass
    try:
        window.update()
    except tkinter._tkinter.TclError:
        break