import socket, threading, os, ast

host = "127.0.0.1"
port_this = 33000
port_other = 33001
buffersize = 2048
Sequence = 0
event = threading.Event()

recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind((host, port_this))
chatter2 = (host, port_other)

print("========= Chat ========")
print("Type \"exit\" to exit chat")

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
            if rec_array[0] == "ACK" and rec_array[1] == Sequence - 1:
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
                print("\n--------------------------------------")
                print("chatter: {}".format(msg))
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
        else:
            my_array.append(message)
            my_array.append(Sequence)
            recv_sock.sendto(str(my_array).encode(), chatter2)
            Sequence += 1
            while not event.wait(timeout=1):
                print("TIme Exceeded, resending")
                recv_sock.sendto(str(my_array).encode(), chatter2)
            	
            	
            
t1 = threading.Thread(target=handle_sends)
t2 = threading.Thread(target=handle_receives)
t1.start()
t2.start()

