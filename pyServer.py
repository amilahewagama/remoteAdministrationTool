import socket
import sys
import time
import threading
import os

#Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
isReady = 1
isRunning = 1
displayPings = 0
doPing = 1
threadsRunning = 1
clients = []
selectedNode = ""

#Bind sockt to address and port and listen for clients
#Enter the current server address
server_address = ('<CURRENT SERVER ADDRESS>', 10000)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)
sock.listen(1)

####COMMAND
def exitServer(args):
    global clients, isReady, isRunning, doPing, sock, threadsRunning
    print("Exiting server...");
    if len(clients) >= 1:
        print("!!--!!Dropping clients!!--!!")
        threadsRunning = 0
        for client in clients:
            print("Dropping client: " , client[1])
            time.sleep(1)
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
def transferClients(args):
    if len(args) >= 0:
        print("Transfering all clients to " + args[0])
        for client in clients:
            time.sleep(1)
            mess = "transfer " + args[0]
            client[0].send(mess.encode())
            client[0].close()
            clients.remove(client)
    else:
        print("Invalid arguments!!! Proper:   transfer <Server address>")
###END transferClients

####COMMAND
def killClient(args):
    if len(args) > 0:
        for client in clients:
            if str(client[1][0]) == args[0]:
                print("\nDropping client: " , client[1])
                client[0].send(b"KILLED")
                client[0].close()
                clients.remove(client)
                print("Done dropping client\n")
    else:
        print("Invalid arguments!!! Proper:   kill <Node address>")
####COMMAND
def showHelp(args):
    print("\n")
    print("----HELP----")
    print("exit  --Drops all clients and stops the server")
    print("node <Node address>  --Drops into nodes shell")
    print("transfer <Server address>  --Transfers all clients to given server address")
    print("list  --Displays all connected clients")
    print("sendAll <Command>  --Sends the command to all nodes")
    print("cl  --Clears the screen")
    print("kill <Node address> --Sends KILLED to node and drops the node. This makes the client permanently disconnect")
    print("help  --Displays help")
###END showHelp

####COMMAND
def clearScreen(args):
    os.system('cls' if os.name == 'nt' else 'clear')
###END of clearScreen

####COMMAND
def sendAll(args):
    if len(args) >= 1:
        args = " ".join(args)
        for client in clients:
            time.sleep(1)
            try:
                client[0].send(args.encode())
            except Exception:
                None
    else:
        print("Invalid arguments!!! Proper:  sendAll <Command>")
###END sendAll


####COMMAND
def selectNode(args):
    global selectedNode
    if len(args) >= 1:
        for client in clients:
            if str(client[1][0]) == args[0]:
                selectedNode = client[1][0]
                print("Node ", client[1][0], " selected! \n")
                print("Run exitN to exit node")
        if selectedNode is "":
            print("Entered node address is invalid", selectedNode)
    else:
        print("Invalid arguments!!! Proper:   node <Node address>")
###END selectNode

def runCommand(command, args):
    methods = { "dispPing" : displayPing , "exit" : exitServer, "list" : listClients, "node" : selectNode, "kill" : killClient, "help" : showHelp, "transfer" : transferClients, "sendAll" : sendAll, "cl" : clearScreen }
    if command in methods:
        methods[command](args) # + argument list of course
    else:
        print("Invalid command!!!")
###END runCommand

def exitNode(args):
    global selectedNode
    if selectedNode != "":
        selectedNode = ""
###END exitNode

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
###END runNode

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
        print("")
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

def socketInput(socketName, socket):
    isRunning = 1
    while isRunning and threadsRunning:

        for client in clients:
            if socketName in client:
                isRunning = 1
            else:
                isRunning = 0

        try:
            mess = socket.recv(1024).decode()
        except Exception as e:
            #print("Client dropped connection :(")
            isRunning = 0
        line = mess.split()
        if len(line) >= 1:
            cmd = line[0]
            line.remove(cmd)
            args = line
            print(mess)
            if str(selectedNode) == str(socketName):
                print(mess)

    #print ("Client recv thread (" , socketName, ") has ended!")
###END socketInput



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
            try:
               clientRecv = threading.Thread(target=socketInput, args=(client_address,connection))
               clientRecv.daemon = 0
               clientRecv.start()
            except Exception:
               print("Error starting client thread: ", Exception.error)

    except Exception:
        print("Error: ", Exception)
import sys; sys.exit()
