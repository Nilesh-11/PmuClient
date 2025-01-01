import pandas as pd
from pydantic import BaseModel 
from Utils.utils import *

def balance_size(phr, dummy):
    mxlen = max([len(sz) for sz in phr])
    for ph in phr:
        while len(ph) < mxlen:
            ph.append(dummy)
    return phr

def process_strings(frame, handle=None):
    dummy = None
    phr = [data.chnam[handle] for data in frame.pmus]
    return balance_size(phr, dummy)

def process_tuples(frame, handle="phasor"):
    dummy = None if handle == "analog" or handle == "digital" else (None, None)
    if handle == "phasor":
        phr = [data.phasors for data in frame.pmu_data]
    elif handle == "analog":
        phr = [data.analog for data in frame.pmu_data]
    elif handle == "digital":
        phr = [data.digital for data in frame.pmu_data]
    elif handle == "phasor_unit":
        phr = [data.phunit for data in frame.pmus]
    elif handle == "analog_unit":
        phr = [data.anunit for data in frame.pmus]
    elif handle == "digital_unit":
        phr = [data.dgunit for data in frame.pmus]
    else:
        raise NotImplementedError(f"Error: Not a measured quanity {handle}.")
    return balance_size(phr, dummy)

def process_dataFrame(frame, cfgFrame):
    
    data = (frame.soc,
            cfgFrame.identifier,
            frame.num_pmu,
            frame.stream_idcode,
            [data.stn for data in cfgFrame.pmus],
            [data.data_idcode for data in cfgFrame.pmus],
            process_strings(cfgFrame, "phasor"),
            process_strings(cfgFrame, "analog"),
            process_strings(cfgFrame, "digital"),
            [data.freq for data in frame.pmu_data],
            [data.rocof for data in frame.pmu_data],
            [data.phnmr for data in frame.pmu_data],
            [data.phr_type for data in frame.pmu_data],
            process_tuples(frame, "phasor"),
            [data.annmr for data in frame.pmu_data],
            process_tuples(frame, "analog"),
            [data.dgnmr for data in frame.pmu_data],
            process_tuples(frame, "digital"),
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

def process_cfg1Frame(cfgFrame):
    data = (cfgFrame.soc,
            cfgFrame.identifier,
            cfgFrame.frame_version,
            cfgFrame.stream_idcode,
            cfgFrame.data_rate,
            cfgFrame.num_pmu,
            [data.stn for data in cfgFrame.pmus],
            [data.data_idcode for data in cfgFrame.pmus],
            [data.phnmr for data in cfgFrame.pmus],
            process_tuples(cfgFrame, "phasor_unit"),
            [data.annmr for data in cfgFrame.pmus],
            process_tuples(cfgFrame, "analog_unit"),
            [data.dgnmr for data in cfgFrame.pmus],
            process_tuples(cfgFrame, "digital_unit"),
            process_strings(cfgFrame, "phasor"),
            process_strings(cfgFrame, "analog"),
            process_strings(cfgFrame, "digital"),
            [data.fnom for data in cfgFrame.pmus],
            [data.cfgcnt for data in cfgFrame.pmus],
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