import socket, threading, os, ast

#declaring our host and ports
host = "127.0.0.1"
port_this = 33000 #We swap the last digit in one of the clients
port_other = 33001 #We swap the last digit in one of the clients
buffersize = 2048 #Size of buffer
Sequence = 0 #the Sequence for the messages that are being sent
event = threading.Event() #A thread event that we will use to handle the messages that are being sent and received
 
 #Binding the socket
recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind((host, port_this))
chatter2 = (host, port_other)
#A meesage to declare that you started the chat
print("========= Chat ========")
print("Type \"exit\" to exit chat")

#Our receive function
def handle_receives():
    global Sequence #It's a global variable because the send function will increment it and the receive function should check by it whether the received Ack is the one being waiting for or not
    old_msg = "" #To check for the duplicates
    old_Seq = 4141524535 #random number to check if it's a duplicate ACK
    while True: #To keep waiting for incoming messages
        #We declare these 3 arrays here to reset them whenever we receives a new message
        rec_array = [] #To cut the received message into an array to see the content + the ack/seq number
        send_array= []#To create the ACK message and send it
        message= [] # The received message
        try:
            message, _ = recv_sock.recvfrom(buffersize) #Receive the message from the socket
            message = message.decode() #Decode the message, since it is being sent in the form of bytes
            msg = message #Not neccassry, but I added for me not get confused
            rec_array = ast.literal_eval(message) #Add the content of message to rec_array, but as an array 
            if rec_array[0] == "ACK" and rec_array[1] == Sequence - 1: #We check if the message is an ACK and if it matches the sequence number of the last chat message (I mean not an ack message) we sent 
                if old_Seq != Sequence -1: #If it's not a duplicate ACK, if its a duplicate just leave it
                   print("\n--------------------------------------")
                   print("chatter Acked the message")
                   print("--------------------------------------")
                   print("\nEnter a new message: ")
                   old_Seq = Sequence -1 #Saving the sequence number and moving forward, so we check the next receiving ACK message if it's matches the old sequence then its a duplicate
                   event.set() #Since we are doing stop and wait, when we send a message we keep waiting till the message sent is ACKED
            elif msg == old_msg: #We are checking if the receiving content message (I mean not an ack message) is a duplicate
                print("Found a duplicate, resending ACK")
                print("\nEnter a new message: \n")
                send_array.append("ACK") #Write the payload of the message as ACK
                send_array.append(rec_array[1]) #Add the sequence number of the content message we just received
                recv_sock.sendto(str(send_array).encode(), chatter2) #Resend the ACK, but the sender didnt receive it and it resent the message, we send as a string bcz sendto takes a string
            elif msg != "": #if it's not an ACK, nor a duplicate, then it's a new content message
                print("\n--------------------------------------")
                print("chatter: {}".format(msg))
                print("--------------------------------------")
                send_array.append("ACK") #Write the payload of the message as ACK
                send_array.append(rec_array[1]) #Add the sequence number of the content message we just received
                recv_sock.sendto(str(send_array).encode(), chatter2) #Send an ACK that you received the content message successfully, we send as a string bcz sendto takes a string
                old_msg = msg #Saving the content of the message to check the upcoming content message if it's a duplicate or not
        except:
            pass
#Our sending function
def handle_sends(): 
    global Sequence #It's a global variable because the send function will increment it and the receive function should check by it whether the received Ack is the one being waiting for or not
    print("Enter a new message: ")
    while True:    #To keep sending new messages
        my_array = [] #the array that we we fill our message content it along with sequence number
        message = input("") #To get the message from the user // I also didnt include Enter a new message, due to the event handling it was better to ask the user to enter a new message whenver we receive a new ACK or each time we receive a content message. When you run the program you'll understand better.It is better looking like this. 
        print("") #Outputting a new empty line
        if message == "exit": #If the input is "exit", the chat will close and the program will terminate
            os._exit(0)
        else:#If it's a normal content
            my_array.append(message) #Add the content of the message to my_array
            my_array.append(Sequence) #Add the sequence number to my_array
            recv_sock.sendto(str(my_array).encode(), chatter2) #Send the content message as a string, since the sendto takes a string
            Sequence += 1 #Increment the sequence number whenever we send a new content message
            while not event.wait(timeout=1): #Here, we keep waiting for the message we sent to be ACKed, then we continue with the code. Whenever we reach the timeout it enters the while body
                print("TIme Exceeded, resending") #Alerting the user that the message took too much time to be Acked
                recv_sock.sendto(str(my_array).encode(), chatter2) #We keep resending the message untill it's Acked
            	
            	
            
t1 = threading.Thread(target=handle_sends) #Assigning a thread to the send function
t2 = threading.Thread(target=handle_receives) #Assigning a thread to the receive function
t1.start() #Starting t1
t2.start() #Starting t2

