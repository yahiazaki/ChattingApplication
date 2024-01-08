import threading
import socket
import time

 
from GlobalVariables import *







def leave_chatroom(client, nicknames,chatrooms,clients):
    for chatroom_name, participants in chatrooms.items():
        if client in participants:
            broadcast(f'{nicknames[clients.index(client)]} left {chatroom_name} chatroom!'.encode('ascii'), client,
                      chatrooms, False)
            participants.remove(client)

            return

def find_chatroom(element, chatrooms, is_rejected):
    if is_rejected:
        # loop on chatrooms that don't start with private
        for chatroom_name, participants in chatrooms.items():
            if not chatroom_name.startswith('private'):
                if element in participants:
                    return chatroom_name
        return None

    else:      
        for chatroom_name, participants in chatrooms.items():
            if element in participants:
                return chatroom_name
        return None

# Broadcast message to all connected clients in a specific chatroom
def broadcast(message, sender, chatrooms, is_private,Credentials=None):
    if is_private and message == "ACCEPTED".encode('ascii'):

        private_keys = [key for key in chatrooms.keys() if key.startswith('private')]
        for key in private_keys:
            print("chatrooms[key]", chatrooms[key])
            if sender in chatrooms[key]:
                for participant in chatrooms[key]:
                    participant.send(message)
    elif is_private and message == "REJECTED".encode('ascii'):
        private_keys = [key for key in chatrooms.keys() if key.startswith('private')]
        if len(private_keys) > 1:
            private_keys = private_keys[1:]
        for key in private_keys:
            if sender in chatrooms[key]:
                for participant in chatrooms[key]:
                    participant.send(message)
                    
                break
    else:
                
        chatroom_name = find_chatroom(sender, chatrooms, False)
        if chatroom_name is not None:
            for participant in chatrooms[chatroom_name]:
                participant.send(message)








# Handle messages from clients
def handle(client, nicknames,chatrooms,clients,Credentials):
    while True:
        try:
            message = client.recv(1024)
            if message.decode('ascii').startswith('/leave'):
                leave_chatroom(client,nicknames,chatrooms,clients)  # Call the function to handle leaving the chat room
            elif "accepted" in message.decode('ascii'):
                print("in accepted")
                leave_chatroom(client,nicknames,chatrooms,clients)  # Call the function to handle leaving the chat room
                broadcast("ACCEPTED".encode('ascii'), client, chatrooms,True,Credentials)
            elif "rejected" in message.decode('ascii'):
                broadcast("REJECTED".encode('ascii'), client, chatrooms,True,Credentials)
                
                
            
            else:
                broadcast(message, client, chatrooms,False,Credentials)

            
        except:
            # index = clients.index(client)
            # clients.remove(client)
            # client.close()
            # nickname = nicknames[index]
            # broadcast('{} left!'.format(nickname).encode('ascii'), client, chatrooms)
            # nicknames.remove(nickname)
            leave_chatroom(client, nicknames, chatrooms, clients)  # Remove client from any chatroom
            break

