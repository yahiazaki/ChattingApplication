import socket
import threading
import sqlite3
import bcrypt
import json
import colorama

from colorama import *
from GlobalVariables import username

colorama.init(autoreset=True)

nickname = input("Enter your nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

HEADER_LENGTH = 10
# conn = sqlite3.connect("userdata.db")
# cur = conn.cursor()

# Lock for thread safety
lock = threading.Lock()

# Event to signal when the client is ready to send messages
ready_to_send = threading.Event()


def is_valid_chatroom(input_text, available_chatrooms):
    parts = input_text.split(' ')

    return len(parts) == 2 and parts[0] == '/join' and parts[1] != '' and parts[1] in available_chatrooms


# Listening to Server and Sending Username
def receive():
    global username
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Username
            message = client.recv(1024).decode('ascii')
            if message == 'Register/Login':
                with lock:
                    choice = int(input("1.login\n2.register\n"))
                    while 1:
                        if choice == 1:
                            username = input("please enter your username: ")
                            password = input("please enter your password: ")

                           # print("in choice 1")

                            """retrieving the password and the associated salt to check the entered password for login in result attribute"""

                            cur.execute("SELECT password, password_salt FROM userdata WHERE username=?", (username,))
                            result = cur.fetchone()
                            #print("result: ",result)

                            if result:

                                stored_hashed_password = result[0]
                                stored_salt = result[1]

                                """Hash the entered password with the retrieved salt"""
                                entered_hashed_password = bcrypt.hashpw(password.encode('utf-8'), stored_salt)

                                if entered_hashed_password == stored_hashed_password:

                                    username_header_login = f'{len(username):<{HEADER_LENGTH}}'.encode('utf-8')
                                    username_text = username.encode('utf-8')
                                    # client.send(username_header_login + username_text)

                                    Password_header_login = f'{len(password):<{HEADER_LENGTH}}'.encode('utf-8')
                                    password_text = password.encode('utf-8')
                                    # client.send(Password_header_login + password_text)
                                    # send both username and password to server as a tuple

                                    message_data = [
                                        "Login",
                                         username_text.decode('utf-8'),
                                         password_text.decode('utf-8')
                                    ]
                                    message_json = json.dumps(message_data).encode('utf-8')

                                    # Send the JSON string
                                    client.send(message_json)
                                    break

                                else:

                                    print('invalid password!')

                            else:

                                print('invalid username or password!\n')

                        elif choice == 2:
                            username = input("please enter your username: ")
                            password = input("please enter your password: ")
                          #  print("in choice 2")

                            """Checkin for the entered username in the database and returning the result in found
                            if found is false then the username is unique else not unique"""
                            cur.execute("SELECT * FROM userdata WHERE username=?", (username,))
                            found = cur.fetchone()
                           # print("found: ", found)

                            if found is None:

                                """Padding 10 to the left to know the length of the username entered,
                                and encoding the username and the padding to send the message to the server"""
                                username_header_register = f'{len(username):<{HEADER_LENGTH}}'.encode('utf-8')
                                username_text = username.encode('utf-8')

                                """Sending the header length and the username to the server"""
                                # client.send(username_header_register + username_text)

                                Password_header_Register = f'{len(password):<{HEADER_LENGTH}}'.encode('utf-8')
                                password_text = password.encode('utf-8')
                                # client.send(Password_header_Register + password_text)

                                """  Signal to the server that the incoming messages pertain to the registration process. """
                                # client.send('register'.encode('utf-8'))
                                message_data = [
                                    "Register",
                                     username_text.decode('utf-8'),
                                     password_text.decode('utf-8')
                                ]
                                message_json = json.dumps(message_data).encode('utf-8')

                                # Send the JSON string
                                client.send(message_json)
                               # print("sent")
                                break
                            else:
                                print('Username is not unique!\n')

                    # client.send(Username.encode('ascii'))
                available_chatrooms = client.recv(1024).decode('ascii')
                print("\nAvailable Chatrooms. To choose a chatroom, enter /join <name of chatroom>: {}".format(
                    available_chatrooms))

                # Take user input to join a chatroom, create a new one, or leave
                while True:
                    message = input()
                    if message.startswith('/join'):
                        if is_valid_chatroom(message, available_chatrooms):
                            with lock:
                                client.send(message.encode('ascii'))
                            break
                        else:
                            print("Please enter /join <name of chatroom> to join a chatroom")
                    elif message.startswith('/create'):
                        _, _, chatroom_name = message.partition('/create ')
                        chatroom_name = chatroom_name.strip()
                        with lock:
                            client.send(message.encode('ascii'))
                        break
                    elif message == '/leave':
                        with lock:
                            client.send(message.encode('ascii'))
                        break  # Send the leave command to the server and break from the loop
                    else:
                        print(
                            "Invalid command. To join, enter /join <name of chatroom>, to create, enter /create <name of chatroom>, to leave, enter /leave")

                # Signal that the client is ready to send messages
                ready_to_send.set()
            else:
                print(message)


        except:
            # Close Connection When Error
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            print("An error occurred!")
            with lock:
                client.close()
            break


def write():
    global username
    print("Waiting for the client to be ready...")
    # Wait for the signal that the client is ready to send messages
    ready_to_send.wait()
    print("Now you can send messages:\n")

    while True:
        message = input('')
        if message == '/leave':
            with lock:
                client.send(message.encode('ascii'))
            break  # Exit the loop if '/leave' is typed
        else:
            message = f'{Fore.LIGHTMAGENTA_EX}{username}:{Fore.LIGHTGREEN_EX}{message}'
            with lock:
                client.send(message.encode('ascii'))

# Start the write thread outside the loop
write_thread = threading.Thread(target=write)
write_thread.start()

# Start the receive thread
receive_thread = threading.Thread(target=receive)
receive_thread.start()
