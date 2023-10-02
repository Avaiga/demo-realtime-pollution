# echo-client.py

from random import randint
import time
import socket
import math
import numpy as np
import pickle

HOST = "127.0.0.1"
PORT = 65432

init_lat = 49.247
init_long = 1.377

factory_lat = 49.246
factory_long = 1.369

random_number = randint(1, 100000)
countdown = 0

lats = []
longs = []
pollutions = []
times = []
max_pollutions = []

diff_lat = abs(init_lat - factory_lat) * 15
diff_long = abs(init_long - factory_long) * 15

lats_unique = np.arange(init_lat - diff_lat, init_lat + diff_lat, 0.001)
longs_unique = np.arange(init_long - diff_long, init_long + diff_long, 0.001)


def pollution(lat, long):
    """
    Return pollution level in percentage
    Pollution should be centered around the factory
    Pollution should decrease with distance to factory
    Pollution should have an added random component
    """
    global countdown
    return 80 * (0.5 + 0.5 * math.sin(countdown / 20)) * math.exp(
        -(0.8 * (lat - factory_lat) ** 2 + 0.2 * (long - factory_long) ** 2) / 0.00005
    ) + np.random.randint(0, 50)


for lat in lats_unique:
    for long in longs_unique:
        lats.append(lat)
        longs.append(long)
        pollutions.append(pollution(lat, long))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        for i in range(len(pollutions)):
            pollutions[i] = pollution(lats[i], longs[i])
        s.sendall(pickle.dumps(pollutions))
        print(f"Sent: {pollutions[:1]}...{pollutions[-1:]}")
        time.sleep(2)
        countdown += 5
