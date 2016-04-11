from socket import *
from tkinter import *
from enum import Enum
from room import Room
import time
from datetime import datetime, date

#round timer value for selecting actions during attack/defend sequences
ROUND_TIME = 30

#wizard stats
MAX_HEALTH = 6
wiz1_points = 0
wiz2_points = 0
current_player = ""
current_attacker = ""


#variables used to calculate timer values
time1 = None
time2 = None
time_delt = None

#connection details
host = '127.0.0.1' #socket.gethostname() # local machine name
port = 12348                # service port

#lobby rooms
roomList = []

#max username size
TEXT_MAXINPUTSIZE = 16

#flags
has_attacks = False
has_defends = False

#message strings
error_message = ""
server_command = ""
build_sequence = ""
attack_sequence = ""
defend_sequence = ""

#variable used for display offset
offset = 0
numActionsSelected = 0

#maximum number of actions during defend/attack
#5 should be the maximum used without modifying the display
MAX_ACTIONS = 5

def addElementalDisplay(top, element, color):
    global offset
    global numActionsSelected
    global MAX_ACTIONS
    global build_sequence
    global has_attacks
    global has_defends

    if numActionsSelected < MAX_ACTIONS:    
        #Action Label
        offset = offset + .15
        actionLabel = Label(top, text= element, justify = LEFT, fg=color)
        actionLabel.place(relx=offset, rely=0.35, anchor=CENTER)

        if build_sequence == "NONE":
            build_sequence = element
        else:
            build_sequence = build_sequence + ";" + element

        if currentStatus == ClientStatus.attacking:
            attack_sequence = build_sequence
        elif currentStatus == ClientStatus.defending:
            defend_sequence = build_sequence
        
        numActionsSelected = numActionsSelected + 1
        if numActionsSelected == MAX_ACTIONS:
            if currentStatus == ClientStatus.attacking:
                has_attacks = True
            elif currentStatus == ClientStatus.defending:
                has_defends = True
    
def updateTimer():
    global time2
    global time_delt
    global timerVar
    global ROUND_TIME
    global has_attacks
    global has_defends
    global s
    global build_sequence
    global nextStatus
    
    if currentStatus == ClientStatus.attacking or currentStatus == ClientStatus.defending:
        time2 = datetime.time(datetime.now())
        time_delt = (datetime.combine(date.today(), time2) - datetime.combine(date.today(), time1)).total_seconds()

        #formats the timer displays to remain on 0 while transitioning states
        if ROUND_TIME - time_delt <= 0:
            time_delt = ROUND_TIME

        #sets a label text variable to update timers on forms
        timerVar.set( str(int(round(ROUND_TIME-time_delt))))

        #timer has ran out, or actions have been confirmed
        if time_delt == ROUND_TIME or has_attacks == True or has_defends == True:
            try:
                if currentStatus == ClientStatus.attacking:
                    s.send(bytes("SEND_ATTACK", "UTF-8"))
                    data = (s.recv(1024)).decode("UTF-8")

                    #dummy test, remove when building server
                    if data == "SEND_ATTACK":
                        data = "OKAY"

                    if data == "OKAY":
                        s.send(bytes(build_sequence, "UTF-8"))
                        data = (s.recv(1024)).decode("UTF-8")

                        #dummy test, remove when building server
                        if data == build_sequence:
                            data = "OKAY"

                        if data == "OKAY":
                            nextStatus = ClientStatus.waiting
                        
                elif currentStatus == ClientStatus.defending:
                    s.send(bytes("SEND_DEFEND", "UTF-8"))
                    data = (s.recv(1024)).decode("UTF-8")

                    #dummy test, remove when building server
                    if data == "SEND_DEFEND":
                        data = "OKAY"

                    if data == "OKAY":
                        s.send(bytes(build_sequence, "UTF-8"))
                        data = (s.recv(1024)).decode("UTF-8")

                        #dummy test, remove when building server
                        if data == build_sequence:
                            data = "OKAY"

                        if data == "OKAY":
                            nextStatus = ClientStatus.waiting
            except timeout:
                err.set("A timeout has occurred")
                s.close()
            except error:
                err.set("An error has occurred")
                s.close()
            
        
def getServerCommand():
    global s
    global currentStatus
    global nextStatus
    global error_message
    global current_player
    global current_attacker
    
    try:
        if currentStatus == ClientStatus.inRoom:
            #data = (s.recv(1024)).decode("UTF-8")

            ##########DUMMY DATA FOR TESTING
            data = "DEFENDING"

            if data == "ATTACKING":
                nextStatus = ClientStatus.attacking
                current_player = "First Player"
                current_attacker = current_player
            elif data == "DEFENDING":
                nextStatus = ClientStatus.defending
                current_player = "Second Player"
            elif data == "SPECTATING":
                nextStatus = ClientStatus.spectating
                current_player = "Spectator"

        if currentStatus == ClientStatus.waiting:
            global has_attacks
            global has_defends
            global attack_sequence
            global defend_sequence

            if has_attacks != True:
                s.send(bytes("GET_ATTACKS", "UTF-8"))
                data = (s.recv(1024)).decode("UTF-8")

                if data == "GET_ATTACKS":
                    data = "NONE"

                #server tells client to wait if the data requested isn't available
                if data != "WAIT":
                    attack_sequence = data
                    has_attacks = True
                    print(attack_sequence)
                else:
                    print("waiting for attack data")
                

            if has_defends != True:
                s.send(bytes("GET_DEFENDS", "UTF-8"))
                data = (s.recv(1024)).decode("UTF-8")

                if data == "GET_DEFENDS":
                    data = "NONE"

                #server tells client to wait if the data requested isn't available
                if data != "WAIT":
                    defend_sequence = data
                    has_defends = True
                    print(defend_sequence)
                else:
                    print("waiting for defend data")

            if has_attacks == True and has_defends == True:
                nextStatus = ClientStatus.playingActions

        if currentStatus == ClientStatus.checkGameState:
            print("checking game state")
            
            
    except timeout:
        error_message = "A timeout has occurred"
        nextStatus = ClientStatus.offline
        s.close()
    except error:
        error_message = "An error has occurred"
        nextStatus = ClientStatus.offline
        s.close()

class ClientStatus(Enum):
    offline = 1
    inLobby = 2
    inRoom = 3
    attacking = 4
    defending = 5
    spectating = 6
    waiting = 7
    playingActions = 8
    checkGameState = 9
    endGame = 10
    noUpdate = 11

currentStatus = ClientStatus.offline
nextStatus = ClientStatus.noUpdate



def mockList():
    firstRoom = Room()
    secondRoom = Room()
    thirdRoom = Room()
    fourthRoom = Room()

    firstRoom.name = "first"
    secondRoom.name = "second"
    thirdRoom.name = "third"
    fourthRoom.name = "fourth"

    roomList.append(firstRoom)
    roomList.append(secondRoom)
    roomList.append(thirdRoom)
    roomList.append(fourthRoom)

def validateTextInputSize(event):
    if (event.widget.index(END) >= TEXT_MAXINPUTSIZE - 1):
        event.widget.delete(TEXT_MAXINPUTSIZE - 1)


def getRoomString(index):
    room = roomList[index]
    return room.name + " {0}".format(room.numPlayers) + "/" + "{0}".format(room.numMax)+"  Players\nSpectators " + "{0}".format(room.spectators)

def loadRooms(first, second, third, index):
    upperIndex = len(roomList) - 1

    if index <= upperIndex:
        first.set(getRoomString(index))
    if index + 1<= upperIndex:
        second.set(getRoomString(index + 1))
    else:
        second.set("")
    if index + 2<= upperIndex:
        third.set(getRoomString(index + 2))
    else:
        third.set("")
    
def loadNext(first, second, third, index, NB, PB):
    if index[0] + 3 <= len(roomList):
        index[0] = index[0] + 3
        PB['state'] = ACTIVE
        if index[0] + 3 > len(roomList):
            NB['state'] = DISABLED
    loadRooms(first, second, third, index[0])

def loadPrior(first, second, third, index, NB, PB):
    if index[0] - 3 >= 0:
        index[0] = index[0] - 3
        NB['state'] = ACTIVE
        if index[0] - 3 < 0:
            PB['state'] = DISABLED
    loadRooms(first, second, third, index[0])

def connectToRoom(command, roomname, err):
    global nextStatus
    global s
    global error_message
    try:
        s.send(bytes(command, "UTF-8"))
        data = (s.recv(1024)).decode("UTF-8")
        print(data)

        #MOCK DATA FOR TESTING PURPOSES PLEASE DELETE WHEN DONE
        ###########
        data = "JOIN_SUCCESS"

        #successful create and/or join
        if data == "JOIN_SUCCESS":
                    
            global wiz1_points
            global wiz2_points
            global MAX_POINTS

            #resets points when room is created
            wiz1_points = 0
            wiz2_points = 0

            nextStatus = ClientStatus.inRoom

        #can't join
        if data == "BAD_JOIN":
            err.set("Cannot join because room is full")
        

        #cannot create
        if data == "ROOM_EXISTS":
            err.set("Cannot create room because it already exists")

        #can spectate (to be added later)

        #error case
        if data == "ERROR":
            nextStatus = ClientStatus.offline
            error_message = "An unknown connection error has occurred\nor the server has kicked you"
            s.close()
        
    except timeout:
        error_message = "A timeout has occurred"
        nextStatus = ClientStatus.offline
        s.close()
    except error:
        error_message = "An error has occurred"
        nextStatus = ClientStatus.offline
        s.close()
        
    
def connectToServer(userName, err):
    #attempts to connect to the server
    #if succesful, checks that the username is free
    global s
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(5)
    try:
        #send userName to server
        
        s.connect((host, port))
        s.send(bytes(userName, "UTF-8"))

        print(userName)
        data = (s.recv(1024)).decode("UTF-8")
        print(data)
            
        if data == "true":
            global nextStatus
            nextStatus = ClientStatus.inLobby
            err.set("")
            #socket stays open in this case
        elif data == "false":
            err.set("That user name is already in use!")
            s.close()
        else:
            err.set("Unknown data was returned from the connection!")
            s.close()
        
    except timeout:
        err.set("A timeout has occurred")
        s.close()
    except error:
        err.set("An error has occurred")
        s.close()

def leaveRoom():
    global s
    global error_message
    global nextStatus

    try:
        s.send(bytes("LEAVE", "UTF-8"))

        data = (s.recv(1024)).decode("UTF-8")
        print(data)

        if data == "LEAVE":
            nextStatus = ClientStatus.inLobby
        
    except timeout:
        error_message = "A timeout has occurred"
        nextStatus = ClientStatus.offline
        s.close()
    except error:
        error_message = "An error has occurred"
        nextStatus = ClientStatus.offline
        s.close()
        
#GUI for Offline Status
def makeOfflineWindow(base, top, socket):
    top = Frame(base)
    top.pack(fill=BOTH, expand=1)

    global error_message
    err = StringVar()
    err.set(error_message)

    connectButton = Button(top, text="Connect", width=12,
                           command= lambda: connectToServer(userNameEntry.get(),
                           err))
    
    connectButton.place(relx=0.5, rely=0.75, anchor=CENTER)

    wwLabel = Label(top, text="Wizard War")
    wwLabel.place(relx=0.5, rely=0.25, anchor=CENTER)

    userNameLabel = Label(top, text="USER NAME : ")
    userNameLabel.place(relx=0.40, rely=0.60, anchor=CENTER)
    
    errorLabel = Label(top, textvariable= err, fg="red")
    errorLabel.place(relx=0.5, rely=0.45, anchor=CENTER)

    userNameEntry = Entry(top)
    userNameEntry.place(relx=0.60, rely=0.60, anchor=CENTER)
    
#GUI for InLobby Status
def makeInLobbyWindow(base, top, s):
    top = Frame(base)
    top.pack(fill=BOTH, expand=1)

    global error_message
    error_message = ""
    err = StringVar()
    err.set(error_message)
    
    #default message
    roomOneVar = StringVar()
    roomOneVar.set("There are currently no rooms\rbut that is cool")
    
    roomTwoVar = StringVar()
    roomTwoVar.set("")
    
    roomThreeVar = StringVar()
    roomThreeVar.set("")

    index = [1]
    index[0] = 0


    #make mock list to test GUI, but would typically get list from server
    mockList()

    roomOneLabel = Label(top, textvariable= roomOneVar, justify = LEFT)
    roomOneLabel.place(relx=0.3, rely=0.15, anchor=W)

    roomTwoLabel = Label(top, textvariable= roomTwoVar, justify = LEFT)
    roomTwoLabel.place(relx=0.3, rely=0.30, anchor=W)

    roomThreeLabel = Label(top, textvariable= roomThreeVar, justify = LEFT)
    roomThreeLabel.place(relx=0.3, rely=0.45, anchor=W)
    

    #load the rooms on creation
    loadRooms(roomOneVar, roomTwoVar, roomThreeVar, index[0])

    
    #make buttons for NEXT/PREVIOUS

    nextButton = Button(top, text=">>>>", width=8,
                           command= lambda: loadNext(roomOneVar, roomTwoVar, roomThreeVar, index, nextButton, previousButton))
    nextButton.place(relx=0.9, rely=0.5, anchor=CENTER)

    #previous button starts greyed out and disabled
    previousButton = Button(top, text="<<<<", width=8, fg="gray",
                           command= lambda: loadPrior(roomOneVar, roomTwoVar, roomThreeVar, index, nextButton, previousButton))
    previousButton.place(relx=0.10, rely=0.5, anchor=CENTER)
    
    previousButton['state'] = DISABLED
    #also disables the next button if there isn't enough entries
    if len(roomList) < 4:
        nextButton['state'] = DISABLED

    #Room Name Label
    roomNameLabel = Label(top, text= "Room Name: ", justify = LEFT)
    roomNameLabel.place(relx=0.3, rely=0.70, anchor=W)

    #Room Name Entry Box
    roomNameEntry = Entry(top)
    roomNameEntry.place(relx=0.48, rely=0.70, anchor=W)
    roomNameEntry.bind("<Key>", validateTextInputSize)

    #Create Button
    createButton = Button(top, text="Create Room", width=32,
                           command= lambda: connectToRoom("CREATE", roomNameEntry.get(), err))
    createButton.place(relx=0.3, rely=0.80, anchor=W)

    #Join Button
    joinButton = Button(top, text="Join Room", width=32,
                           command= lambda: connectToRoom("JOIN", roomNameEntry.get(), err))
    joinButton.place(relx=0.3, rely=.90, anchor=W)

    #Error Label
    errorLabel = Label(top, textvariable= err, justify = LEFT, fg="red")
    errorLabel.place(relx=0.3, rely=0.60, anchor=W)

def makeInRoomWindow(base, top, s):
    top = Frame(base)
    top.pack(fill=BOTH, expand=1)

    global error_message
    error_message = ""
    err = StringVar()
    err.set(error_message)

    #Error Label
    errorLabel = Label(top, textvariable= err, justify = LEFT, fg="red")
    errorLabel.place(relx=0.3, rely=0.60, anchor=W)

    #message Label
    messageLabel = Label(top, text="WAITING FOR OTHER PLAYERS TO JOIN", justify = LEFT)
    messageLabel.place(relx=0.3, rely=0.25, anchor=W)

    #Leave Button
    leaveButton = Button(top, text="Leave Room", width=24,
                           command= lambda: leaveRoom())
    leaveButton.place(relx=0.33, rely=.75, anchor=W)

def makeWaitingWindow(base, top, s):
    top = Frame(base)
    top.pack(fill=BOTH, expand=1)

    global error_message
    error_message = ""
    err = StringVar()
    err.set(error_message)

    #Error Label
    errorLabel = Label(top, textvariable= err, justify = LEFT, fg="red")
    errorLabel.place(relx=0.3, rely=0.60, anchor=W)

    #message Label
    messageLabel = Label(top, text="WAITING FOR OTHER PLAYER...", justify = LEFT)
    messageLabel.place(relx=0.3, rely=0.25, anchor=W)

def makeAttackingWindow(base, top, s):
    top = Frame(base)
    top.pack(fill=BOTH, expand=1)

    global error_message
    global timerVar
    global offset
    global build_sequence
    build_sequence = "NONE"
    attack_sequence = ""
    defend_sequence = ""
    
    timerVar.set("30")
    error_message = ""
    err = StringVar()
    err.set(error_message)

    offset = 0.10

    #Error Label
    errorLabel = Label(top, textvariable= err, justify = LEFT, fg="red")
    errorLabel.place(relx=0.50, rely=0.63, anchor=CENTER)
    
    #Attack Directions Label
    attackLabel = Label(top, text= "ATTACKING - Please select up to 5 attacks", justify = LEFT)
    attackLabel.place(relx=0.50, rely=0.10, anchor=CENTER)

    #Timer Label
    timerLabel = Label(top, textvariable= timerVar, justify = LEFT, fg="red")
    timerLabel.place(relx=0.50, rely=0.20, anchor=CENTER)

    #Sequence Label
    sequenceLabel = Label(top, text= "Action Sequence: ", justify = LEFT)
    sequenceLabel.place(relx=offset, rely=0.35, anchor=CENTER)

    #Fire Button
    fireButton = Button(top, text="Fire", width=16,
                           command= lambda: addElementalDisplay(top, "Fire", "red"))
    fireButton.place(relx=0.15, rely=.75, anchor=CENTER)

    #Water Button
    waterButton = Button(top, text="Water", width=16,
                           command= lambda: addElementalDisplay(top, "Water", "blue"))
    waterButton.place(relx=0.50, rely=.75, anchor=CENTER)

    #Electric Button
    electricButton = Button(top, text="Electric", width=16,
                           command= lambda: addElementalDisplay(top, "Electric", "orange"))
    electricButton.place(relx=0.85, rely=.75, anchor=CENTER)



def makeDefendingWindow(base, top, s):
    top = Frame(base)
    top.pack(fill=BOTH, expand=1)

    global error_message
    global timerVar
    global offset
    global build_sequence
    build_sequence = "NONE"
    attack_sequence = ""
    defend_sequence = ""
    
    timerVar.set("30")
    error_message = ""
    err = StringVar()
    err.set(error_message)

    offset = 0.10

    #Error Label
    errorLabel = Label(top, textvariable= err, justify = LEFT, fg="red")
    errorLabel.place(relx=0.50, rely=0.63, anchor=CENTER)
    
    #Defending Directions Label
    attackLabel = Label(top, text= "DEFENDING - Please select up to 5 defenses", justify = LEFT)
    attackLabel.place(relx=0.50, rely=0.10, anchor=CENTER)

    #Timer Label
    timerLabel = Label(top, textvariable= timerVar, justify = LEFT, fg="red")
    timerLabel.place(relx=0.50, rely=0.20, anchor=CENTER)

    #Sequence Label
    sequenceLabel = Label(top, text= "Action Sequence: ", justify = LEFT)
    sequenceLabel.place(relx=offset, rely=0.35, anchor=CENTER)

    #Fire Button
    fireButton = Button(top, text="Fire", width=16,
                           command= lambda: addElementalDisplay(top, "Fire", "red"))
    fireButton.place(relx=0.15, rely=.75, anchor=CENTER)

    #Water Button
    waterButton = Button(top, text="Water", width=16,
                           command= lambda: addElementalDisplay(top, "Water", "blue"))
    waterButton.place(relx=0.50, rely=.75, anchor=CENTER)

    #Electric Button
    electricButton = Button(top, text="Electric", width=16,
                           command= lambda: addElementalDisplay(top, "Electric", "orange"))
    electricButton.place(relx=0.85, rely=.75, anchor=CENTER)
    
def updateGUI(base, top, sock):
    global nextStatus
    global currentStatus
    global time1
    if nextStatus != ClientStatus.noUpdate:
        print(nextStatus)
        time.sleep(1)
        for child in base.winfo_children():
            child.destroy()
        print(nextStatus)
        if nextStatus == ClientStatus.offline:
            makeOfflineWindow(base, top, sock)
        if nextStatus == ClientStatus.inLobby:
            makeInLobbyWindow(base, top, sock)
        if nextStatus == ClientStatus.inRoom:
            makeInRoomWindow(base, top, sock)
        if nextStatus == ClientStatus.attacking:
            makeAttackingWindow(base, top, sock)
            time1 = datetime.time(datetime.now())
        if nextStatus == ClientStatus.defending:
            makeDefendingWindow(base, top, sock)
            time1 = datetime.time(datetime.now())
        if nextStatus == ClientStatus.waiting:
            makeWaitingWindow(base, top, sock)
            
        currentStatus = nextStatus
        nextStatus = ClientStatus.noUpdate
            


base = Tk()
topFrame = None

timerVar = StringVar()
timerVar.set("")

#setup client window
base.resizable(width=False, height=False)
base.geometry('{}x{}'.format(600, 450))
base.title("Wizard War")


s = None         # create socket
makeOfflineWindow(base, topFrame, s)


while True:
    global currentStatus
    
    base.update_idletasks()
    base.update()
    updateGUI(base, topFrame, s)
    getServerCommand()
    updateTimer()


'''
host = '127.0.0.1' #socket.gethostname() # local machine name
port = 12348                # service port


s.connect((host, port))
'''

if s != None:
    s.close() 
