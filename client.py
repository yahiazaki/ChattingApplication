import bcrypt
import socket
import sqlite3
import sys
import colorama
import msvcrt
import errno
from colorama import *

colorama.init(autoreset=True)

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 12345

"""Creating a TCP connection for the client on address 127.0.0.1 and port 12345"""
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

conn = sqlite3.connect("userdata.db")
cur = conn.cursor()

"""User Register Function, requires a unique username """


def register(username, password):
    """Checkin for the entered username in the database and returning the result in found
    if found is false then the username is unique else not unique"""
    cur.execute("SELECT * FROM userdata WHERE username=?", (username,))
    found = cur.fetchone()

    if found is None:

        """Padding 10 to the left to know the length of the username entered,
        and encoding the username and the padding to send the message to the server"""
        username_header_register = f'{len(username):<{HEADER_LENGTH}}'.encode('utf-8')
        username_text = username.encode('utf-8')

        """Sending the header length and the username to the server"""
        client_socket.send(username_header_register + username_text)

        Password_header_Register = f'{len(password):<{HEADER_LENGTH}}'.encode('utf-8')
        password_text = password.encode('utf-8')
        client_socket.send(Password_header_Register + password_text)

        """  Signal to the server that the incoming messages pertain to the registration process. """
        client_socket.send('register'.encode('utf-8'))
        return True

    else:
        print('Username is not unique!')
        return False


def login(username, password):
    """retrieving the password and the associated salt to check the entered password for login in result attribute"""
    cur.execute("SELECT password, password_salt FROM userdata WHERE username=?", (username,))
    result = cur.fetchone()

    if result:

        stored_hashed_password = result[0]
        stored_salt = result[1]

        """Hash the entered password with the retrieved salt"""
        entered_hashed_password = bcrypt.hashpw(password.encode('utf-8'), stored_salt)

        if entered_hashed_password == stored_hashed_password:

            username_header_login = f'{len(username):<{HEADER_LENGTH}}'.encode('utf-8')
            username_text = username.encode('utf-8')
            client_socket.send(username_header_login + username_text)

            Password_header_login = f'{len(password):<{HEADER_LENGTH}}'.encode('utf-8')
            password_text = password.encode('utf-8')
            client_socket.send(Password_header_login + password_text)

            client_socket.send('login'.encode('utf-8'))
            return True

        else:

            print('invalid password!')
            return False

    else:

        print('invalid username or password!')
        return False


choice = input("1.login\n2.register\n")

if choice == '2':
    R_result = False
    while not R_result:
        my_username = input("Enter Unique Username: ")
        my_password = input("Create Password: ")
        R_result = register(my_username, my_password)
else:
    L_result = False
    while not L_result:
        my_username = input("Enter Username: ")
        my_password = input("Enter Password: ")
        L_result = login(my_username, my_password)

while True:

    """If there is any pressed key then start reading input"""
    if msvcrt.kbhit():
        message = input(f'{Fore.LIGHTMAGENTA_EX}{my_username} >{Fore.LIGHTGREEN_EX} ')
        if message:
            message_header = f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')
            message = message.encode('utf-8')
            client_socket.send(message_header + message)
    try:
        while True:

            """receiving the username header of clients sent in the broadcast of the server"""
            username_header = client_socket.recv(HEADER_LENGTH)

            if not username_header:
                print('connection closed by the server')
                sys.exit()

            """decoding the username to be readable"""
            username_length = int(username_header.decode('utf-8').strip())
            username_data = client_socket.recv(username_length).decode('utf-8')

            """decoding the message received from the server to be readable"""
            message_header_received = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header_received.decode('utf-8').strip())
            message_received = client_socket.recv(message_length).decode('utf-8')

            print(f'{username_data} > {message_received}')

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
        continue

    except Exception as e:
        print('Reading error: '.format(str(e)))
        sys.exit()
