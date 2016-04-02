import socket
from socket import error as SocketError

import _thread
import errno

s = socket.socket()         # create socket
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allow socket reuse

host = '127.0.0.1' #socket.gethostname() # local machine name
port = 12348                # service port
s.bind((host, port))

s.listen(5)

def clientThread(conn):
     while True:
         try:
             conn.send(bytes('Hi! I am server\n', 'UTF-8'))
             data = (conn.recv(1024)).decode("utf-8")
             print(data)
         except SocketError as e:
             if e.errno == errno.ECONNRESET:
                 pass


while True:
   conn, addr = s.accept()     # connect to client
   print('Connected to: ', addr)
   _thread.start_new_thread(clientThread,(conn,))

            
conn.close()                
s.close()
