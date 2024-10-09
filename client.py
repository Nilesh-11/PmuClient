from frames import *
from utils import *
import socket
import pandas as pd

class client(object):
    FRAME_TYPES = {
        0: dataFrame,
        1: headerFrame,
        2: cfg1,
        3: cfg1,
        5: cfg1,
        4: commandFrame
    }
    
    def __init__(self, ADDR, data_lim=2048):
        self.data_lim = data_lim
        self.data = pd.DataFrame(columns=['Time', 'Frame type', 'Frame size', 'pmu index', 'Frequency', 'ROCOF'])
        self.addr = ADDR
        self.cfg = None
        self.header = None
        self.command = None
    
    def receive(self, time=10):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(self.addr)
        except socket.error as e:
            print(f"Socket error : {e}")
        while True:
            try:
                data = client.recv(self.data_lim)
                if len(data) == 0:
                    print("Received empty data.")
                    break
                self.update_data(data)
            except socket.error as e:
                print(f"Socket errror : {e}")
            except:
                print("Error in receiving data.")
                break
        print(self.cfg)
            
    def update_data(self, data):
        frame_type = self.get_frame_type(data[0:2])
        if frame_type == 0:
            assert self.cfg != None, "Configuration frame not found."
            frame = client.FRAME_TYPES[frame_type](data, 
                                                   pmuinfo = self.cfg.pmus,
                                                   time_base = self.cfg.time_base,
                                                   num_pmu = self.cfg.num_pmu)
            print(frame)
            self.save_dataFrame(frame)
        elif frame_type & 2 != 0 or frame_type == 5:
            self.cfg = cfg1(data)
        elif frame_type == 1:
            self.header = headerFrame(data)
        elif frame_type == 4:
            self.command = commandFrame(data)
        else:
            print("Not a suitable frametype")

    def save_dataFrame(self, frame):
        rows = []
        for i in range(len(frame.pmu_data)):
            row = {
                'Time':frame.time, 
                'Frame type': frame.frame_type, 
                'Frame size': frame.framesize, 
                'pmu index' : i,
                'Frequency' : frame.pmu_data[i].freq,
                'ROCOF': frame.pmu_data[i].rocof
                }
            rows.append(row)
                
        rows = pd.DataFrame(rows)
        self.data = pd.concat([self.data, rows], ignore_index=True)
        pass
    
    def save_data(self):
        self.data.to_csv('output.csv')
    
    def get_frame_type(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        return int(data[8:12], 2)
            
    