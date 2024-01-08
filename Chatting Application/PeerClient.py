import socket
import threading
import sqlite3
import bcrypt
import json
import colorama

from colorama import *
from GlobalVariables import *

colorama.init(autoreset=True)

nickname = input("Enter your nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

HEADER_LENGTH = 10


# Lock for thread safety
lock = threading.Lock()

# Event to signal when the client is ready to send messages
ready_to_send = threading.Event()





def is_valid_chatroom(input_text, available_chatrooms):
    parts = input_text.split(' ')

    return len(parts) == 2 and parts[0] == '/join' and parts[1] != '' and parts[1] in available_chatrooms

def handle_room(msg,choice):
    global username

    while True:

        print("1. connect to a private chatroom\n2. connect to a group chatroom\n")
        choice = int(input())
        if choice == 1:
            client.send("PRIVATE".encode('ascii'))
            msg = client.recv(1024).decode('ascii')
            if 'person' in msg:
                print(msg)
                while True:
                    person_name = input()
                    # check that the format is like this person_name : <name>,
                    # and that the name is not empty
                    if person_name.startswith('person_name : ') and person_name != 'person_name : ':
                        break
                    else:
                        print("Please enter the name of the person you want to chat with this format person_name : <name>")
                    
                client.send(person_name.encode('ascii'))
                msg = client.recv(1024).decode('ascii')
                while True:
                    if 'Offline' in msg:
                        print(msg)
                        person_name = input()
                        client.send(person_name.encode('ascii'))
                        msg = client.recv(1024).decode('ascii')
                    else:
                        print(msg)
                        break
            break

                


        elif choice == 2:
            client.send("GROUP".encode('ascii'))
            available_chatrooms = client.recv(1024).decode('ascii')

            while True:
                print(f"\nAvailable Chatrooms. To choose a chatroom, enter /join {available_chatrooms} ,\n to create a chatroom enter /create <name> \n to leave enter /leave: \n")
                message = input()
                if message.startswith('/join'):
                    if is_valid_chatroom(message, available_chatrooms):
                        
                        client.send(message.encode('ascii'))
                        break
                    else:
                        print("Please enter /join <name of chatroom> to join a chatroom")
                elif message.startswith('/create'):
                    client.send(message.encode('ascii'))
                    break
                elif message == '/leave':
                    
                    print("You can't leave the chatroom before joining it")
                    continue  
                else:
                    print(
                        "Invalid command. To join, enter /join <name of chatroom>, to create, enter /create <name of chatroom>, to leave, enter /leave")
            break
        
        else:
            print("invalid choice")
            continue

# Listening to Server and Sending Username
def receive():
    global username
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()
    while True:
        try:
        
            message = client.recv(1024).decode('ascii')
            if message == 'Register/Login':
                with lock:
                    
                    while 1:
                        choice = int(input("1.login\n2.register\n"))
                        if choice == 1:
                            username = input("please enter your username: ")
                            password = input("please enter your password: ")


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

                                    Password_header_login = f'{len(password):<{HEADER_LENGTH}}'.encode('utf-8')
                                    password_text = password.encode('utf-8')
                                   
                                    message_data = [
                                        "Login",
                                         username_text.decode('utf-8'),
                                         password_text.decode('utf-8'),
                                         nickname
                                    ]
                                    message_json = json.dumps(message_data).encode('utf-8')

                                    # Send the JSON string
                                    client.send(message_json)
                                    break

                                else:

                                    print('invalid password!')
                                    continue

                            else:

                                print('invalid username or password!\n')
                                continue

                        elif choice == 2:
                            username = input("please enter your username: ")
                            password = input("please enter your password: ")

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

                                Password_header_Register = f'{len(password):<{HEADER_LENGTH}}'.encode('utf-8')
                                password_text = password.encode('utf-8')

                                """  Signal to the server that the incoming messages pertain to the registration process. """
                                message_data = [
                                    "Register",
                                     username_text.decode('utf-8'),
                                     password_text.decode('utf-8'),
                                     nickname
                                ]
                                message_json = json.dumps(message_data).encode('utf-8')

                                # Send the JSON string
                                client.send(message_json)
                               # print("sent")
                                break
                            else:
                                print('Username is not unique!\n')
                                continue
                        else:
                            print("invalid choice")
                            continue
               
                    msg = client.recv(1024).decode('ascii')
                    if msg == 'ROOM':
                        handle_room(msg,choice)
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
                print("Closing connection...")
                client.close()
            break


def write():
    global username
    print("Waiting for the client to be ready...")
    # Wait for the signal that the client is ready to send messages
    ready_to_send.wait()

    while True:
        # Check if the write thread is enabled
            message = input('')
            if message == '/leave':
                with lock:
                    client.send(message.encode('ascii'))
                break
            elif message == '1':
                client.send("Request accepted".encode('ascii'))
            elif message == '2':
                client.send("Request rejected".encode('ascii'))
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
