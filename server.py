import socket
import threading

import select
import sqlite3

from DB import insert_user

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()

"""Creating client dictionary to hold client data"""
client = {}

print(f'-->Listening for connection on {IP}:{PORT}')

"""Receiving client data"""
def receive_message(client_socket):
    try:

        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False


conn = sqlite3.connect("userdata.db")
cur = conn.cursor()


def Client_Thread(client_socket, client_address):
    count = 0
    user = receive_message(client_socket)
    if user is False:
        return
    client[client_socket] = user
    count += 1
    print('Accepted connection from {}:{} username:{}'.format(*client_address, user['data'].decode('utf-8')))

    while True:

        if count == 1:

            password = receive_message(client_socket)
            usr = client[client_socket]
            result = client_socket.recv(1024).decode('utf-8')

            if result == 'register':

                """if client is sending a registration form, server is inserting user data in the database"""
                insert_user(usr['data'].decode('utf-8'), password['data'].decode('utf-8'))
                print('-->registed for user:{}'.format(usr['data'].decode('utf-8')))\

            else:
                print(f"-->received password from {usr['data'].decode('utf-8')}:{password['data'].decode('utf-8')}")

            count = 0

        else:
            message = receive_message(client_socket)

            if message is False:
                print('-->closed connection from client {}'.format(client[client_socket]['data'].decode('utf-8')))
                break

            usr = client[client_socket]
            print(f"received message from {usr['data'].decode('utf-8')}:{message['data'].decode('utf-8')}")

            """broadcasting the received message to all client in the same chat"""
            for socket in client:
                if socket != client_socket:
                    socket.send(usr['header'] + usr['data'] + message['header'] + message['data'])

    client_socket.close()


"""Creating a new thread for each client establishing connection"""
while True:
    client_socket, client_address = server_socket.accept()
    thread = threading.Thread(target=Client_Thread, args=(client_socket, client_address))
    thread.start()
