# echo-client.py

from random import randint
import time
import socket

HOST = "127.0.0.1"
PORT = 65432 

random_number = randint(1, 100000)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        s.sendall(str(random_number).encode())
        random_number += randint(0, 50)
        print(random_number)
        time.sleep(5)
    
