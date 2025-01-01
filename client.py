from protocol.frames import *
from Utils.utils import *
from Utils.process_frames import *
import socket
import pandas as pd
import os

FRAME_TYPES = {
    0: dataFrame,
    1: headerFrame,
    2: cfg1,
    3: cfg1,
    4: commandFrame,
    5: cfg1
}

class dbDataFrame:
    time: str
    identifier: str
    num_pmu: int
    stream_id: int

class client(object):
    
    def __init__(self, ADDR, dbUser, data_lim=2048):
        self.data_lim = data_lim
        self.data = pd.DataFrame(columns=['Time', 'Frame type', 'Frame size', 'pmu index', 'Frequency', 'ROCOF'])
        self.addr = ADDR
        self.cfg = None
        self.header = None
        self.command = None
        self.dbUser = dbUser
    
    def receive(self, time=10):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(self.addr)
        except socket.error as e:
            raise ConnectionError(f"Socket error : {e}")
        while True:
            try:
                data = client.recv(self.data_lim)
                if len(data) == 0:
                    print("Received empty data...quitting")
                    break
                self.update_data(data)
            except socket.error as e:
                raise ConnectionError(f"Socket errror : {e}")
            except:
                raise RuntimeError("Error in receiving data.")
    
    def update_data(self, data):
        frame_type = get_frame_type(data[0:2])
        assert not(frame_type & 2 != 0 or frame_type == 5) and self.cfg != None, "Configuration frame not found."
        if frame_type == 0:
            frame = dataFrame(data, 
                              pmuinfo = self.cfg.pmus,
                              time_base = self.cfg.time_base,
                              num_pmu = self.cfg.num_pmu)
            save_dataFrame_csv(frame)
        elif frame_type & 2 != 0 or frame_type == 5:
            self.cfg = cfg1(data)
            self.cfg.identifier = generate_unique_identifier(self.addr[0], self.addr[1])
        elif frame_type == 1:
            self.header = headerFrame(data)
        elif frame_type == 4:
            self.command = commandFrame(data)
        else:
            raise NotImplementedError("Not a suitable frametype")
  