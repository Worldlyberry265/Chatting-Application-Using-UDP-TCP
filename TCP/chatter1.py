import socket, threading, os, ast
from random import randint

host = "127.0.0.1"
port_this = 33000
port_other = 33001
buffersize = 2048
Sequence = 0
event = threading.Event()

recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind((host, port_this))
file_send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
file_recv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
file_recv_sock.bind((host, port_this))
chatter2 = (host, port_other)

if os.name == "nt":
    os.system("cls")
else:
    os.system("clear")

print("========= Chat ========")
print("Type \"exit\" to exit chat")
print("Type $SEND <file-path> to send file")

def send_file(path: str):
    file_send_sock.connect(chatter2)#establishes connection
    file = open(path, "rb")#opens the file specified
    type = path.split(".")[1]#splits the path to path and file type
    data = file.read()#reads file
    file_send_sock.send(type.encode())#sends the type of the file
    file_send_sock.sendall(data)#sends all file bytes
    file_send_sock.send(b"<END>")#sends <END> to signify the end of the file
    file_send_sock.close()

def tcp_recv():
    
    client, _ = file_recv_sock.accept()#accepts connection
    type = client.recv(1024).decode()#receives type from peer
    name = "received-"+str(randint(0, 100))+"."+type
    file = open(name, "wb")#generates random name for file received
    file_bytes = b""#creates empty bytes array
    
    done = False
    while not done:
        data = client.recv(1024)#receives file bytes from peer
        if file_bytes[-5:] == b"<END>":#if data received ends with <END> set done to true  
            done = True
        else:
            file_bytes += data#else append to the bytes array the bytes received
    file.write(file_bytes)#writes the bytes received to the file opened
    file.close()#closes file
    client.close()#closes sender
    print(f"File {name} received")#alerts that file received


def handle_receives():
    global Sequence
    old_msg = ""
    old_Seq = 421; #random number
    while True:
        rec_array = []
        send_array= []
        message= []
        try:
            message, _ = recv_sock.recvfrom(buffersize)
            message = message.decode()
            msg = message
            rec_array = ast.literal_eval(message)
            if rec_array[0] == "ACK" and rec_array[1] == Sequence - 1: #and msg != old_msg
                if old_Seq != Sequence -1:
                   print("\n--------------------------------------")
                   print("chatter Acked the message")
                   print("--------------------------------------")
                   print("\nEnter a new message: ")
                   old_Seq = Sequence -1
                   event.set()
            elif msg == old_msg:
                print("Found a duplicate, resending ACK")
                print("\nEnter a new message: \n")
                send_array.append("ACK")
                send_array.append(rec_array[1])
                recv_sock.sendto(str(send_array).encode(), chatter2)
            elif msg != "":
                ready_msg = msg.split(",")
                print("\n--------------------------------------")
                print("chatter: {}".format(ready_msg[0][1:]))
                print("--------------------------------------")
                send_array.append("ACK")
                send_array.append(rec_array[1])
                recv_sock.sendto(str(send_array).encode(), chatter2)
                old_msg = msg
        except:
            pass

def handle_sends():
    global Sequence
    my_array = []
    print("Enter a new message: ")
    while True:    
        my_array = []
        message = input("")
        print("")
        if message == "exit":
            os._exit(0)
        elif message[0:5] == "$SEND":
            send_statement = message.split(" ", 1)
            send_file(send_statement[1])

        else:
            my_array.append(message)
            my_array.append(Sequence)
            recv_sock.sendto(str(my_array).encode(), chatter2)
            Sequence += 1
            while not event.wait(timeout=1):
                print("TIme Exceeded, resending")
                recv_sock.sendto(str(my_array).encode(), chatter2)
            	

def handle_file():
    while True:
        file_recv_sock.listen()
        tcp_recv()

t1 = threading.Thread(target=handle_sends)
t2 = threading.Thread(target=handle_receives)
t3 = threading.Thread(target=handle_file)
t1.start()
t2.start()
t3.start()

