import threading
import socket
import time

from GlobalVariables import *
def find_chatroom(element, chatrooms):
    for chatroom_name, participants in chatrooms.items():
        if element in participants:
            return chatroom_name
    return None

# Broadcast message to all connected clients in a specific chatroom
def broadcast(message, sender, chatrooms):
    chatroom_name = find_chatroom(sender, chatrooms)

    if chatroom_name is not None:
        for participant in chatrooms[chatroom_name]:
            participant.send(message)



def leave_chatroom(client, nicknames,chatrooms,clients):
    for chatroom_name, participants in chatrooms.items():
        if client in participants:
            broadcast(f'{nicknames[clients.index(client)]} left {chatroom_name} chatroom!'.encode('ascii'), client,
                      chatrooms)
            participants.remove(client)
          #remove the current nickname from nicknames
            # nicknames.remove(nicknames[clients.index(client)])
            # print("nicknames after removing", nicknames)
            # client.remove(clients)
            return


# Handle messages from clients
def handle(client, nicknames,chatrooms,clients):
    while True:
        try:
            message = client.recv(1024)
            if message.decode('ascii').startswith('/leave'):
                leave_chatroom(client,nicknames,chatrooms,clients)  # Call the function to handle leaving the chat room
            else:
                broadcast(message, client, chatrooms)
        except:
            # index = clients.index(client)
            # clients.remove(client)
            # client.close()
            # nickname = nicknames[index]
            # broadcast('{} left!'.format(nickname).encode('ascii'), client, chatrooms)
            # nicknames.remove(nickname)
            leave_chatroom(client, nicknames, chatrooms, clients)  # Remove client from any chatroom
            break