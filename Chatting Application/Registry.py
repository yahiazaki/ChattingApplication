import json
import threading
import socket
import time
import sqlite3

from GlobalVariables import *
from PeerServer import broadcast, handle
from DB import insert_user

host = '127.0.0.1'
port = 55555

conn = sqlite3.connect("userdata.db")
cur = conn.cursor()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()




        
    



def create_chatroom(client, chatroom_name, chatrooms):
    if chatroom_name not in chatrooms:
        chatrooms[chatroom_name] = [client]
        client.send(f'You created the {chatroom_name} chatroom!'.encode('ascii'))
        broadcast(f'New chatroom "{chatroom_name}" created!'.encode('ascii'), client, chatrooms,False)
    else:
        client.send('Chatroom already exists!'.encode('ascii'))



def join_chatroom(client, chatroom_name, chatrooms, nicknames):
    if chatroom_name in chatrooms:
        chatrooms[chatroom_name].append(client)
        print("Someone joined the chatroom")
        broadcast(f'{nicknames[clients.index(client)]} joined {chatroom_name} chatroom!'.encode('ascii'), client,
                  chatrooms,False)
    else:
        client.send('Chatroom does not exist!'.encode('ascii'))


# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

       
        client.send('Register/Login'.encode('ascii'))
        Credentials = client.recv(1024).decode('utf-8')
           
        
        Credentials = json.loads(Credentials) 
        print("Received data:", Credentials)
        print("Credentials[0]", Credentials[0])
        if Credentials[0] == 'Register':
            print(f"credentials[0] is register")
            """if client is sending a registration form, server is inserting user data in the database"""
            insert_user(Credentials[1], Credentials[2])
            nicknames.append(Credentials[1])  # Append the nickname to the list
            clients.append(client)
            print('-->registered for user:{}'.format(Credentials[1]))

        elif Credentials[0] == 'Login':
                nicknames.append(Credentials[1])  # Append the nickname to the list
                clients.append(client)
                print(f"-->received password from {Credentials[1]}:{Credentials[2]}")

        client.send("ROOM".encode('ascii'))

        msg = client.recv(1024).decode('ascii')
        
        if msg == 'PRIVATE':
                client.send("Enter the username of the person you want to chat with this format person_name : <name>".encode('ascii'))
                person_name = client.recv(1024).decode('ascii')
                person_name = person_name.split(':')
                person_name = person_name[1].strip()
                
                # search for the person in the clients list
                while True:
                    if person_name in nicknames:
                        client.send("User Online, waiting for user's Acceptance".encode('ascii'))
                        break
                    else:
                        client.send("User Offline".encode('ascii'))
                        person_name = client.recv(1024).decode('ascii')
                        person_name = person_name.split(':')
                        person_name = person_name[1].strip()
                
                # get the index of the person in the clients list using the index of the nickname
                index = nicknames.index(person_name)
                
                
                # send a msg to the other user asking if they want to chat
                print("Sending chat request to {}".format(clients[index]))
                clients[index].send("You have a chat request from {} 1. Accept  2. Reject".format(Credentials[1]).encode('ascii'))
                chatroom_name = f'private_{Credentials[1]}_{person_name}'
                chatrooms[chatroom_name] = [client, clients[index]]
                
                thread = threading.Thread(target=handle, args=(client, nicknames, chatrooms, clients,Credentials,))
                thread.start()
                
                        

        elif msg == 'GROUP':
                    print("sending chatrooms to client")
                    client.send(','.join(chatrooms.keys()).encode('ascii'))
                    chatroom = client.recv(1024).decode('ascii')
                    print("msg after GROUP IS", chatroom)
                    if chatroom.startswith('/join'):
                        _, _, chatroom_name = chatroom.partition('/join ')
                        chatroom_name = chatroom_name.strip()
                        print("clients list", clients)
                        join_chatroom(client, chatroom_name, chatrooms, nicknames)
                    elif chatroom.startswith('/create'):
                        _, _, chatroom_name = chatroom.partition('/create ')
                        chatroom_name = chatroom_name.strip()
                        create_chatroom(client, chatroom, chatrooms)
                    else:
                        client.send('Invalid command!'.encode('ascii'))
                        client.send('Connected to server!'.encode('ascii'))
                    thread = threading.Thread(target=handle, args=(client, nicknames, chatrooms, clients,Credentials))
                    thread.start()
       
         

        
        

print("Server is listening...")
receive()