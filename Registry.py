import json
import threading
import socket
import time
import sqlite3

from GlobalVariables import nicknames, chatrooms, clients
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
        broadcast(f'New chatroom "{chatroom_name}" created!'.encode('ascii'), client, chatrooms)
    else:
        client.send('Chatroom already exists!'.encode('ascii'))


def join_chatroom(client, chatroom_name, chatrooms, nicknames):
    if chatroom_name in chatrooms:
        chatrooms[chatroom_name].append(client)
        # print("Someone joined the chatroom")
        broadcast(f'{nicknames[clients.index(client)]} joined {chatroom_name} chatroom!'.encode('ascii'), client,
                  chatrooms)
    else:
        client.send('Chatroom does not exist!'.encode('ascii'))


# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('Register/Login'.encode('ascii'))
        Credentials = client.recv(1024).decode('utf-8')
        Credentials = json.loads(Credentials)
        # print(Credentials)

        if Credentials[0] == 'Register':
            """if client is sending a registration form, server is inserting user data in the database"""
            insert_user(Credentials[1], Credentials[2])
            # print("User Data Sent")
            nicknames.append(Credentials[1])  # Append the nickname to the list
            clients.append(client)
            print('-->registered for user:{}'.format(Credentials[1]))

        elif Credentials[0] == 'Login':
            nicknames.append(Credentials[1])  # Append the nickname to the list
            clients.append(client)
            print(f"-->received password from {Credentials[1]}:{Credentials[2]}")

        # broadcast("{} joined!".format(nickname).encode('ascii'))

        client.send(','.join(chatrooms.keys()).encode('ascii'))
        chatroom = client.recv(1024).decode('ascii')
        if chatroom.startswith('/join'):
            _, _, chatroom_name = chatroom.partition('/join ')
            chatroom_name = chatroom_name.strip()
            join_chatroom(client, chatroom_name, chatrooms, nicknames)
        elif chatroom.startswith('/create'):
            _, _, chatroom_name = chatroom.partition('/create ')
            chatroom_name = chatroom_name.strip()
            create_chatroom(client, chatroom_name, chatrooms)
        else:
            client.send('Invalid command!'.encode('ascii'))
            client.send('Connected to server!'.encode('ascii'))
        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client, nicknames, chatrooms, clients))
        thread.start()


print("Server is listening...")
receive()
