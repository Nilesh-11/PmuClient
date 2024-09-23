from frames import *
import socket
from bitarray import bitarray

HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
PORT = 7027
SERVER = '10.32.14.87'
ADDR = (SERVER, PORT)


if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(10)
    frames = []
    FRAME_TYPES = {
        0: dataFrame,
        1: headerFrame,
        2: cfg1,
        3: cfg1
    }
    try:
        client.connect(ADDR)
    except socket.error as e:
        print(f"Socket error : {e}")

    while True:
        try:
            data = client.recv(2048)
            print(data)
        except:
            print("Error in receiving data.")
            break