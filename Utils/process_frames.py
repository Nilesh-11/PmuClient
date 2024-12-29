import pandas as pd
from pydantic import BaseModel 
from Utils.utils import *

def process_dataFrame(frame, cfgFrame):
    data = (frame.soc,
            cfgFrame.identifier,
            frame.num_pmu,
            frame.stream_idcode,
            [data.stn for data in cfgFrame.pmus],
            [data.data_idcode for data in cfgFrame.pmus],
            [data.chnam["phasor"] for data in cfgFrame.pmus],
            [data.chnam["analog"] for data in cfgFrame.pmus],
            [data.chnam["digital"] for data in cfgFrame.pmus],
            [data.freq for data in frame.pmu_data],
            [data.rocof for data in frame.pmu_data],
            [data.phnmr for data in frame.pmu_data],
            [data.phr_type for data in frame.pmu_data],
            [data.phasors for data in frame.pmu_data],
            [data.annmr for data in frame.pmu_data],
            [data.analog for data in frame.pmu_data],
            [data.dgnmr for data in frame.pmu_data],
            [data.digital for data in frame.pmu_data],
            [data.data_error for data in frame.pmu_data],
            [data.time_quality for data in frame.pmu_data],
            [data.PMU_sync for data in frame.pmu_data],
            [data.trigger_reason for data in frame.pmu_data],
            )
    return data

def save_dataFrame_csv(frame, filepath=None):
    data = pd.DataFrame(columns=['Time', 'Frame type', 'Frame size', 'pmu index', 'Frequency', 'ROCOF'])
    rows = []
    for i in range(len(frame.pmu_data)):
        row = {
            'Time':frame.time, 
            'Frame type': frame.frame_type, 
            'Frame size': frame.framesize, 
            'pmu index' : i,
            'Frequency' : frame.pmu_data[i].freq,
            'ROCOF': frame.pmu_data[i].rocof,
            'phr': frame.pmu_data[i].phasors[0]
            }
        rows.append(row)
    rows = pd.DataFrame(rows)
    data = pd.concat([data, rows], ignore_index=True)
    data.to_csv('./Results/output.csv')

def process_cfg1Frame(frame):
    data = (frame.soc,
            frame.identifier,
            frame.frame_version,
            frame.stream_idcode,
            frame.data_rate,
            frame.num_pmu,
            [data.stn for data in frame.pmus],
            [data.data_idcode for data in frame.pmus],
            [data.phnmr for data in frame.pmus],
            [data.phunit for data in frame.pmus],
            [data.annmr for data in frame.pmus],
            [data.anunit for data in frame.pmus],
            [data.dgnmr for data in frame.pmus],
            [data.dgunit for data in frame.pmus],
            [data.chnam["phasor"] for data in frame.pmus],
            [data.chnam["analog"] for data in frame.pmus],
            [data.chnam["digital"] for data in frame.pmus],
            [data.fnom for data in frame.pmus],
            [data.cfgcnt for data in frame.pmus],
            )
    return data

def save_cfg1Frame():
    pass

def save_headerFrame():
    pass

def save_commandFrame():
    pass

def get_frame_type(data: str):
    data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
    return int(data[9:12], 2)