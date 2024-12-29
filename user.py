from client import *
import os
from dotenv import load_dotenv
from Utils.utils import *
from DatabaseManager import *
load_dotenv()

dbmanager = DatabaseManager(
            host=os.environ.get('DBHOST'),
            port=os.environ.get('DBPORT'),
            database=os.environ.get('DBNAME'),
            user=os.environ.get('DBUSERNAME'),
            password=os.environ.get('DBPASSWORD')
        )

LOCALSERVER = os.environ.get('LOCALSERVER')
LOCALPORT = int(os.environ.get('LOCALPORT'))
ADDR = (LOCALSERVER, LOCALPORT)

user = client(ADDR, dbmanager)

user.receive()

plot_figure('Results/output.csv')