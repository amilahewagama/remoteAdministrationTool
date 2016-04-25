import socket
import sys
import time
import threading

#Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
isReady = 1
isRunning = 1
displayPings = 0
doPing = 1
clients = []
selectedNode = ""

#Bind sockt to address and port and listen for clients
server_address = ('192.168.1.8', 10000)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)
sock.listen(1)

####COMMAND
def exitServer(args):
    global clients, isReady, isRunning, doPing, sock
    print("Exiting server...");
    if len(clients) >= 1:
        print("!!--!!Dropping clients!!--!!")
        for client in clients:
            print("Dropping client: " , client[1])
            client[0].send(b"DROPPED")
            client[0].close()
            clients.remove(client)
        print("==--==Done dropping clients==--==")
    isReady = 0
    selectedNode = ""
    print("Closing server socket")
    sock.close()
    print("Socket closed...")
    k = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    k.connect(server_address)
    k.close()
    print("Stopping threads")
    isReady = 0
    doPing = 0
    isRunning = 0
    sock = None
    exit(0)
###END exitServer

####COMMAND
def displayPing(args):
    global displayPings
    if len(args) >= 1:
        if args[0] == "true":
            displayPings = 1
            print("Now displaying pings")
        elif args[0] == "false":
            displayPings = 0
            print("Stopped displaying pings")
        else:
            print("Invalid arguments! Proper:   dispPing <true / false>")
###END displayPings

####COMMAND
def listClients(args):
    for client in clients:
        print(client[1])
###END listClients

####COMMAND
def selectNode(args):
    global selectedNode
    if len(args) >= 1:
        for client in clients:
            print(args[0])
            print(client[1][0])
            if str(client[1][0]) == args[0]:
                selectedNode = client[1][0]
                print("Node ", client[1][0], " selected!")
        if selectedNode is "":
            print("Entered node address is invalid", selectedNode)
    else:
        print("Invalid arguments!!! Proper:   node <Node address>")

def runCommand(command, args):
    methods = { "dispPing" : displayPing , "exit" : exitServer, "list" : listClients, "node" : selectNode }
    if command in methods:
        methods[command](args) # + argument list of course
    else:
        print("Invalid command!!!")
###END runCommand

def exitNode(args):
    global selectedNode
    if selectedNode != "":
        selectedNode = ""

def runNode(command, args):
    methods = {"exitN" : exitNode}
    if command in methods:
        methods[command](args) # + argument list of course
    else:
        nodeSocket = ""
        for client in clients:
            if str(client[1][0]) is selectedNode:
                nodeSocket = client[0]
        args = ' '.join(args)
        mess = (command + " " + args).encode()
        nodeSocket.send(mess)
###END runCommand


#Function that manages clients and dropped clients
def pingClients():
    global selectedNode
    while doPing:
        time.sleep(2)
        for client in clients:
            if displayPings is 1:
                print("pinging: ", client[1])
            try:
                client[0].send(b"PING")
            except Exception as e:
                if selectedNode is str(client[1][0]):
                    selectedNode = ""
                client[0].close()
                clients.remove(client)
                print("Dropped ", client[1], "   ", str(e))
    return
###END pingClients


def inputFunc():
    while isRunning:
        prefix = selectedNode + ">"
        line = input(prefix)
        line = line.split()
        if len(line) >= 1:
            cmd = line[0]
            line.remove(cmd)
            args = line
            #print("Command: ", cmd)
            #print("Args: ", args)
            if selectedNode is "":
                runCommand(cmd, args)
            else:
                runNode(cmd, args)
    return
###END inputFunc







#Start client managemet thread
try:
   clientPinger = threading.Thread(target=pingClients)
   inputThread = threading.Thread(target=inputFunc)
   inputThread.daemon = 0
   clientPinger.daemon = 0
   clientPinger.start()
   inputThread.start()
except Exception:
   print("Error: ", Exception.error)

#Accept incoming connections if server is ready
print("Wating for connections ;)")
while isReady:
    connection, client_address = sock.accept()
    try:
        if isReady:
            print( 'connection from ', client_address)
            clients.append([connection, client_address])
    except Exception:
        print("Error: ", Exception)
import sys; sys.exit()
