from client import *
import os
from dotenv import load_dotenv

load_dotenv()

SERVER = os.environ.get('SERVER')
PORT = int(os.environ.get('PORT'))
ADDR = (SERVER, PORT)

user = client(ADDR)

user.receive()
user.save_data()