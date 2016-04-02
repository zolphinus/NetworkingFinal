import socket
import tkinter as tk
from enum import Enum

class ClientStatus(Enum):
    offline = 1
    inLobby = 2
    inRoom = 3
    attacking = 4
    defending = 5
    playingActions = 6
    checkGameState = 7
    endGame = 8

top = tk.Tk()

#setup client window
top.resizable(width=False, height=False)
top.geometry('{}x{}'.format(600, 450))
top.title("Wizard War")

top.mainloop()




s = socket.socket()         # create socket
host = '127.0.0.1' #socket.gethostname() # local machine name
port = 12348                # service port

s.connect((host, port))


'''
while True:
    data = (s.recv(1024)).decode("utf-8")
    print(data)
    s.send(bytes('client', "UTF-8"))
'''

s.close 
