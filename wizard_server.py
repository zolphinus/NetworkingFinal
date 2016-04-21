import socket
from socket import error as SocketError

import _thread
import threading
import errno
import time
from datetime import datetime, date
from random import randint


lock = threading.Lock()

class Room():
     def __init__(self):
          pass
     room_name = ""
     player_1 = None
     player_2 = None
     spectators = []
     time = None
     attack_list = ""
     defend_list = ""
     attacking_player = ""
     hasAttacks = False
     hasDefends = False

class Player():
     def __init__(self, user_name, conn, time):
          self.user_name = user_name
          self.conn = conn
          self.time = time

def leaveRoom(room_name, current_player):
     global room_list
     
     for Item in room_list:
          if room_name == Item.room_name:
               if Item.player_1 == current_player:
                    Item.player_1 = None
               elif Item.player_2 == current_player:
                    Item.player_2 = None
               else:
                    Item.spectators.remove(current_player)


     
def getRole(room_name, current_player):
     global room_list
     
     for Item in room_list:
          if room_name == Item.room_name:
               if Item.player_1 != None and Item.player_2 != None:                         
                    for SPECT in Item.spectators:
                         if SPECT == current_player:
                              return "SPECTATING"

                    if Item.attacking_player == current_player.user_name:
                         return "ATTACKING"
                    else:
                         return "DEFENDING"
     return "WAIT"

def joinRoom(room_name, current_player):
     global room_list
     current_room = None
     for Item in room_list:
          if room_name == Item.room_name:
               current_room = Item
               if Item.player_1 == None:
                    Item.player_1 = current_player
               elif Item.player_2 == None:
                    Item.player_2 = current_player
                    determine_player = randint(0,1)
                    if determine_player == 0:
                         Item.attacking_player = current_room.player_1.user_name
                    else:
                         Item.attacking_player = current_room.player_2.user_name
                    
               else:
                    Item.spectators.append(current_player)
     return current_room
               
s = socket.socket()         # create socket
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allow socket reuse

host = '127.0.0.1' #socket.gethostname() # local machine name
port = 12348                # service port
s.bind((host, port))

s.listen(5)


user_list = []
room_list = []

def roomLookUpName(room_name):
     global room_list
     if len(room_list) > 0:          
          for Item in room_list:
               if room_name == Item.room_name:
                    return True
     return False
     
def lookUpName(user_name):
     global user_list
     if len(user_list) > 0:          
          for Item in user_list:
               if user_name == Item.user_name:
                    return True
     return False

def makeNewUser(user_name, conn):
     global user_list
     tempTime = datetime.time(datetime.now())
     tempUser = Player(user_name, conn, tempTime)
     user_list.append(tempUser)
     return tempUser
     

def clientThread(conn):
     global room_list
     current_player = None
     
     current_room = Room()
     in_room = False
     
     while True:
         try:
             data = (conn.recv(1024)).decode("UTF-8")

             if data == "SEND_USERNAME":
                  ####confirm and await username
                  data = "OKAY"
                  conn.send(bytes(data, 'UTF-8'))
                  user_name = (conn.recv(1024)).decode("UTF-8")
                  user_exists = lookUpName(user_name)
                  print(user_exists)
                  if user_exists:
                       data = "FALSE"
                  else:
                       current_player = makeNewUser(user_name, conn)
                       data = "TRUE"
                  conn.send(bytes(data, 'UTF-8'))
                  #####need to handle room data transfer here
                  
             if data == "CREATE":
                  data = "OKAY"
                  conn.send(bytes(data, 'UTF-8'))
                  room_name = (conn.recv(1024)).decode("UTF-8")
                  room_exists = roomLookUpName(room_name)
                  if room_exists:
                       data = "ROOM_EXISTS"
                  else:
                       current_room.room_name = room_name
                       current_room.player_1 = current_player
                       current_room.time = datetime.time(datetime.now())
                       
                       room_list.append(current_room)
                       data = "JOIN_SUCCESS"
                       in_room = True
                  conn.send(bytes(data, 'UTF-8'))

             if data == "JOIN":
                  data = "OKAY"
                  conn.send(bytes(data, 'UTF-8'))
                  room_name = (conn.recv(1024)).decode("UTF-8")
                  room_exists = roomLookUpName(room_name)
                  if room_exists:
                       current_room = joinRoom(room_name, current_player)
                       data = "JOIN_SUCCESS"
                       in_room = True
                  else:
                       data = "BAD_JOIN"
                  conn.send(bytes(data, 'UTF-8'))

             while in_room == True:
                  data = (conn.recv(1024)).decode("UTF-8")
                  if data == "LEAVE":
                       with lock:
                            leaveRoom(room_name, current_player)
                            data = "LEAVE"
                            in_room = False
                            conn.send(bytes(data, 'UTF-8'))

                  if data == "GET_ROLE":
                       data = getRole(room_name, current_player)
                       conn.send(bytes(data, 'UTF-8'))

                  if data == "SEND_ATTACK":
                       data = "OKAY"
                       conn.send(bytes(data, 'UTF-8'))
                       current_room.attack_list = (conn.recv(1024)).decode("UTF-8")
                       data = "OKAY"
                       conn.send(bytes(data, 'UTF-8'))
                       current_room.hasAttacks = True

                  if data == "GET_ATTACKS":
                       if current_room.hasAttacks:
                            data = current_room.attack_list
                       else:
                            data = "WAIT"
                       conn.send(bytes(data, 'UTF-8'))

                  if data == "GET_DEFENDS":
                       if current_room.hasDefends:
                            data = current_room.defend_list
                       else:
                            data = "WAIT"
                       conn.send(bytes(data, 'UTF-8'))

                  if data == "NEW_ROUND":
                       data = "OKAY"
                       conn.send(bytes(data, 'UTF-8'))
                       data = (conn.recv(1024)).decode("UTF-8")
                       conn.send(bytes(data, 'UTF-8'))
                       current_room.hasAttacks = False
                       current_room.hasDefends = False
                       
                       
                       
                  

                  if data == "SEND_DEFEND":
                       data = "OKAY"
                       conn.send(bytes(data, 'UTF-8'))
                       current_room.defend_list = (conn.recv(1024)).decode("UTF-8")
                       data = "OKAY"
                       conn.send(bytes(data, 'UTF-8'))
                       current_room.hasDefends = True
                       
         except SocketError as e:
             if e.errno == errno.ECONNRESET:
                 pass
               


while True:
   conn, addr = s.accept()     # connect to client
   print('Connected to: ', addr)
   _thread.start_new_thread(clientThread,(conn,))

            
conn.close()                
s.close()
