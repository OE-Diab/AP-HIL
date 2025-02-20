import socket
import time
import random
import datetime
import random

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import socket
import threading


def client_program():
    host = socket.gethostname()  # as both code is running on same pc
    port = 5002  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect(('127.0.0.1', 34000))  # connect to the server

    message ='' #input(" -> ")  # take input

    while message.lower().strip() != 'bye':
        message ="in-"+str(random.uniform(0, 40))+' '
        client_socket.send(message.encode())  # send message
        message = "bg-" + str(random.uniform(0, 400))+' '
        client_socket.send(message.encode())  # send message
        message = "me-" + str(random.uniform(0, 200))+' '
        client_socket.send(message.encode())  # send message
        message = "ti-" + datetime.datetime.now().strftime('%H:%M:%S')+' '
        client_socket.send(message.encode())
       # data = client_socket.recv(1024).decode()  # receive response

       # print('Received from server: ' + data)  # show in terminal

        #message = input(" -> ")  # again take input
        time.sleep(10)

    client_socket.close()



client_program()
