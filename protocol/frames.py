from abc import ABCMeta
from Utils.utils import *
from struct import pack, unpack

class commonFrame(metaclass=ABCMeta):
    FRAME_TYPES = { "data": 0, "header": 1, "cfg1": 2, "cfg2": 3, "cfg3": 5, "cmd": 4 }
    FRAME_TYPES_WORDS = { code: word for word, code in FRAME_TYPES.items() }
    
    def __init__(self, data):
        self.get_SYNC(data[0:2])
        self.get_FRAMESIZE(data[2:4])
        self.get_IDCODE(data[4:6])
        self.get_SOC(data[6:10])
        self.get_FRACSEC(data[10:14])
        pass
    
    def get_SYNC(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.frame_type = int(data[9:12], 2)
        self.frame_version = int(data[12:16], 2)
        pass
    
    def get_FRAMESIZE(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.framesize = int(data, 2)
        pass
    
    def get_IDCODE(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.stream_idcode = int(data, 2)
        pass
    
    def get_SOC(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.soc = int(data, 2)
        pass
    
    def get_FRACSEC(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.msg_tq = int(data[24:32])
        self.fracsec = int(data[0:24], 2)
        pass
    
    def get_CHK(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.chk = int(data, 2)
        pass
    
    def __str__(self):
        return f"""\
FRAME INFORMATION 
* Frame Version : {self.frame_version}
* Frame Type : {commandFrame.FRAME_TYPES_WORDS[self.frame_type]}
* Frame size : {self.framesize}
* Stream ID Code : {self.stream_idcode}
* SOC : {self.soc}
* Time quality : {self.msg_tq}
* FRACSEC : {self.fracsec}\n
    """

class pmuCfg(object):
    
    def __init__(self, data, start):
        self.start = start
        self.get_STN(data[start : start + 16])
        start += 16
        self.get_Data_IDCODE(data[start : start + 2])
        start += 2
        self.get_FORMAT(data[start : start + 2])
        start += 2
        self.get_PHNMR(data[start : start + 2])
        start += 2
        self.get_ANNMR(data[start : start + 2])
        start += 2
        self.get_DGNMR(data[start : start + 2])
        start += 2
        len = 16 * (self.phnmr + self.annmr + self.dgnmr * 16)
        self.get_CHNAM(data[start : start + len])
        start += len
        self.get_PHUNIT(data[start : start + 4 * self.phnmr])
        start += 4 * self.phnmr
        self.get_ANUNIT(data[start : start + 4 * self.annmr])
        start += 4 * self.annmr
        self.get_DIGUNIT(data[start : start + 4 * self.dgnmr])
        start += 4 * self.dgnmr
        self.get_FNOM(data[start : start + 2])
        start += 2
        self.get_CFGCNT(data[start : start + 2])
        start += 2
        self.end = start
        pass
    
    def get_STN(self, data):
        self.stn = data.decode('ascii', errors='ignore')
        pass
    
    def get_Data_IDCODE(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.data_idcode = int(data, 2)
        assert 1 <= self.data_idcode <= 65534, f"data idcode = {self.data_idcode} is out of range (1, 65534)"
    
    def get_FORMAT(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        data = data[::-1]
        self.format = data[0:4]
    
    def get_PHNMR(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.phnmr = int(data, 2)
        assert 0 <= self.phnmr <= 65535, f"Number of phasors = {self.phnmr} is out of range (0, 65535)" 
    
    def get_ANNMR(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.annmr = int(data, 2)
        assert 0 <= self.annmr <= 65535, f"Number of analog phasors = {self.annmr} is out of range (0, 65535)" 
    
    def get_DGNMR(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.dgnmr = int(data, 2)
        assert 0 <= self.dgnmr <= 65535, f"Number of digital phasors = {self.dgnmr} is out of range (0, 65535)" 
    
    def get_CHNAM(self, data):
        def parse(data):
            return data.decode('utf-8', errors='ignore')
        self.chnam = {
            "phasor": [],
            "analog": [],
            "digital": []
        }
        # print(self.phnmr, self.annmr, self.dgnmr)
        cur = 0
        for i in range(self.phnmr):
            phname = data[cur : cur + 16]
            self.chnam["phasor"].append(parse(phname))
            cur += 16
        for i in range(self.annmr):
            anname = data[cur : cur + 16]
            self.chnam["analog"].append(parse(anname))
            cur += 16
        for i in range(self.dgnmr):
            dgnames = []
            for _ in range(16):
                dgname = data[cur : cur + 16]
                dgnames.append(parse(dgname))
                cur += 16
            self.chnam["digital"].append(parse(dgnames))
        return cur
    
    def get_PHUNIT(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.phunit = []
        start = 0
        for i in range(self.phnmr):
            _data = data[start: start + 32]

            if self.format[3] != '0':
                scale = None
            else:
                scale = unpack("!h", pack("!H", int(_data[8:32], 2)))[0]
                scale *= 1e-5
            
            assert scale == None or 0 <= scale <= 16777215, f"scale of phasor = {scale} is out of range (0, 16777215)"
            
            phasor_type = int(_data[0:8], 2)
            if phasor_type != 0:
                res = scale, "i"
            else:
                res =  scale, "v"
            start += 32
            self.phunit.append(res)
    
    def get_ANUNIT(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.anunit = []
        TYPES = { "0": "pow", "1": "rms", "2": "peak" }
        start = 0
        for i in range(self.annmr):
            _data = data[start: start + 32]
            
            analog_type = int(_data[0:8], 2)
            scale = int(_data[8:32], 2)
            
            assert -8388608 <= scale <= 8388608, f"scale of AnalogUnit = {scale} is out of range (-8388608, 8388608)"

            res = scale, TYPES[analog_type]  
            start += 32
            self.anunit.append(res)

    def get_DIGUNIT(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.dgunit = []
        start = 0
        for i in range(self.dgnmr):
            word1 = data[start : start + 16]
            start += 16
            word2 = data[start : start + 16]
            start += 16
            res = word1, word2
            self.dgunit.append(res)

    def get_FNOM(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.fnom = 60 if data[0] == '0' else 50 

    def get_CFGCNT(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.cfgcnt = int(data, 2)
    
    def __str__(self):
        res = f'''
\t- Station Name: {self.stn}
\t- Data stream code: {self.data_idcode}
\t- Phasor Units: {self.phunit}
\t- Analog Units: {self.anunit}
\t- Digital Units: {self.dgunit}
    '''
        res += f"\t- Phasors:- {self.phnmr}\n"
        for i in range(len(self.chnam['phasor'])):
            res += f"\t\t{i}: {self.chnam['phasor'][i]}\n"

        res += f"\t- Analog:- {self.annmr}\n"
        for i in range(len(self.chnam['analog'])):
            res += f"\t\t{i}: {self.chnam['analog'][i]}\n"

        res += f"\t- Digital:- {self.dgnmr}\n"
        for i in range(len(self.chnam['digital'])):
            res += f"\t\t{i}: {self.chnam['digital'][i]}\n"
        return res

class cfg1(commonFrame):
    def __init__(self, data):
        super().__init__(data[0:14])
        self.get_TIME_BASE(data[14:18])
        self.get_NUM_PMU(data[18:20])
        self.pmus = []
        start = 20
        for i in range(self.num_pmu):
            ipmu = pmuCfg(data, start)
            start = ipmu.end
            self.pmus.append(ipmu)

        self.data_rate = self.get_DATA_RATE(data[start : start + 2])
        start += 2
        self.chk = self.get_CHK(data[start : start + 2])
        start += 2
        self.ok = (start == self.framesize)
        assert start == self.framesize,  "Error in extracting frame details"
    
    def get_TIME_BASE(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.time_base = int(data[0:24], 2)
    
    def get_NUM_PMU(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.num_pmu = int(data, 2)
    
    def get_DATA_RATE(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        return int(data, 2)
    
    def __str__(self):
        res = super().__str__()
        res += f'''
Time Base: {self.time_base}
Data rate: {self.data_rate}
Numbers of pmus: {self.num_pmu}
        '''
        for i in range(len(self.pmus)):
            res += f"PMU ID : {i}"
            res += str(self.pmus[i])
        return res
    
class pmuData(object):
    
    MEASUREMENT_STATUS = { "ok": 0, "error": 1, "test": 2, "verror": 3 }
    MEASUREMENT_STATUS_WORDS = { code: word for word, code in MEASUREMENT_STATUS.items() }

    UNLOCKED_TIME = { "<10": 0, "<100": 1, "<1000": 2, ">1000": 3 }
    UNLOCKED_TIME_WORDS = { code: word for word, code in UNLOCKED_TIME.items() }

    TIME_QUALITY = { "n/a": 0, "<100ns": 1, "<1us": 2, "<10us": 3, "<100us": 4, "<1ms": 5, "<10ms": 6, ">10ms": 7}
    TIME_QUALITY_WORDS = { code: word for word, code in TIME_QUALITY.items() }

    TRIGGER_REASON = { "manual": 0, "magnitude_low": 1, "magnitude_high": 2, "phase_angle_diff": 3,
                    "frequency_high_or_log": 4, "df/dt_high": 5, "reserved": 6, "digital": 7 }
    TRIGGER_REASON_WORDS = { code: word for word, code in TRIGGER_REASON.items() }

    def __init__(self, data, start, phnmr, annmr, dgnmr, format):
        self.start = start
        self.phnmr = phnmr
        self.annmr = annmr
        self.dgnmr = dgnmr
        self.format = format
        
        self.phr_type = ('rectangular' if format[0] == '0' else 'polar')
        self.phr_datatype = ('int' if format[1] == '0' else 'float')
        self.ang_datatype = ('int' if format[2] == '0' else 'float')
        self.freq_datatype = ('int' if format[3] == '0' else 'float')
        self.freq_bits = (2 if self.freq_datatype == 'int' else 4)
        self.ang_bits = (2 if self.ang_datatype == 'int' else 4)
        self.phr_bits = (4 if self.phr_datatype == 'int' else 8)
        
        self.data_bits_len = 2 + self.phr_bits * phnmr + self.freq_bits * 2 + self.ang_bits * annmr + 2 * dgnmr
        self.phasors = []
        
        self.get_STAT(data[start : start + 2])
        start += 2
        
        self.get_PHASORS(data[start : start + self.phr_bits * self.phnmr])
        start += self.phr_bits * self.phnmr

        self.get_FREQ(data[start : start + self.freq_bits])
        start += self.freq_bits
        
        self.get_DFREQ(data[start : start + self.freq_bits])
        start += self.freq_bits
        
        self.get_ANALOG(data[start : start + self.ang_bits * self.annmr])
        start += self.ang_bits * self.annmr

        self.get_DIGITAL(data[start : start + 2 * self.dgnmr])
        start += 2 * self.dgnmr
        self.end = start

    def get_STAT(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.is_triggered = True if int(data[11], 2) else False
        self.sorting = "arrival" if int(data[11], 2) else "time stamp"
        self.config_change = (data[10] == '1')
        self.is_modified = (data[9] == '1')
        self.data_error = pmuData.MEASUREMENT_STATUS_WORDS[int(data[14:16], 2)]
        self.trigger_reason = pmuData.TRIGGER_REASON_WORDS[int(data[0:4], 2)]
        self.unlocked_time = pmuData.UNLOCKED_TIME_WORDS[int(data[4:6], 2)]
        self.time_quality = pmuData.TIME_QUALITY_WORDS[int(data[6:9], 2)]
        self.PMU_sync = True if int(data[13], 2) else False
        return

    def get_PHASORS(self, data):
        for i in range(self.phnmr):
            start = i * self.phr_bits
            end = start + self.phr_bits

            val = ''.join(bin(byte)[2:].zfill(8) for byte in data[start : end])
            val = int(val, 2).to_bytes((len(val) + 7) // 8, byteorder="big")

            if self.format[1] == '1':
                val = unpack("!ff", val)
            elif self.phr_type == 'polar':
                val = unpack("!Hh", val)
            else:
                val = unpack("!hh", val)
            val = (float(val[0]), float(val[1]))
            self.phasors.append(val)
    
    def get_FREQ(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        data = int(data, 2)
        if self.freq_datatype == 'float':
            self.freq = unpack('!f', pack('!I', data))[0]
        else:
            self.freq = unpack("!h", pack("!H", data))[0]

    def get_DFREQ(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        data = int(data, 2)
        if self.freq_datatype == 'float':
            self.rocof = unpack('!f', pack('!I', data))[0]
        else:
            self.rocof = unpack("!h", pack("!H", data))[0]

    def get_ANALOG(self, data):
        self.analog = []
        for i in range(self.annmr):
            start = i * (2 if self.ang_datatype == 'int' else 4)
            end = start + (2 if self.ang_datatype == 'int' else 4)
            _data = data[start: end]
            if self.ang_datatype == 'float':
                _data = unpack('!f', pack('!I', _data))[0]
            else:
                _data = unpack("!h", pack("!H", data))[0]
            _data = float(_data)
            self.analog.append(_data)
    
    def get_DIGITAL(self, data):
        self.digital = []
        for i in range(self.dgnmr):
            start = i * 2
            end = start + 2
            _data = data[start: end]
            if self.ang_datatype == 'float':
                _data = unpack('!f', pack('!I', _data))[0]
            else:
                _data = unpack("!h", pack("!H", data))[0]
            _data = float(_data)
            self.digital.append(_data)
            
    def __str__(self):
        return f"""
    - Data Error: {self.data_error}
    - Sorted by: {self.sorting}
    - Trigger detected: {self.is_triggered}
    - Trigger Reason: {self.trigger_reason}
    - Time Quality: {self.time_quality}
    - Unlocked Time: {self.unlocked_time}
    - PMU Sync: {self.PMU_sync}
    - Frequency: {self.freq}
    - ROCOF: {self.rocof}
    - Phasors: {self.phasors}
    - Analog: {self.analog}
    - Digital: {self.digital}
        """
class dataFrame(commonFrame):
    
    def __init__(self, data, pmuinfo, time_base=1000000, num_pmu=1):
        '''
        data = byte (0, 1, 2 ... bit)
        '''
        super().__init__(data[0:14])
        self.start = 14
        self.time_base = time_base
        self.time = self.soc + self.fracsec / self.time_base
        self.num_pmu = num_pmu
        self.pmu_data = []
        self.start = 14
        for i in range(num_pmu):
            ipmu = pmuData(data, self.start, pmuinfo[i].phnmr, pmuinfo[i].annmr, pmuinfo[i].dgnmr, pmuinfo[i].format)
            self.start = ipmu.end
            self.pmu_data.append(ipmu)

        self.get_CHK(data[-2:])
        self.start += 2
        self.ok = (self.start == self.framesize)
        assert self.start == self.framesize, f"Error in extracting frame details, start:{self.start} != framesize:{self.framesize}"
        
        pass
    
    def __str__(self):
        res = super().__str__()
        res += "FRAME CONTENT \n"
        res += f"""\b
Time: {soc_to_dateTime(self.soc)}
PMU data:-
    """
        for i in range(len(self.pmu_data)):
            res += f"PMU ID {i} : {self.pmu_data[i]}\n"
        return res

class headerFrame(commonFrame):
    
    def __init__(self, data):
        super.__init__(data[0:14])
        self.info = data[14: self.framesize - 3].decode('ascii', errors='ignore')
        self.get_CHK(data[-2:0])
        pass
    
    
class commandFrame(commonFrame):
    
    CMD_MSG = {
        1: 'Turn off transmission of data frames.',
        2: 'Turn on transmission of data frames.',
        3: 'Send HDR frame.',
        4: 'Send CFG-1 frame.',
        5: 'Send CFG-2 frame.',
        6: 'Send CFG-3 frame.',
        7: 'Undefined',
        8: 'Extended frame.'
    }
    
    def __init__(self, data):
        super().__init__(data[0:14])
        self.get_CMD(data[14:16])
        self.get_EXTFRAME(data[16:self.framesize - 3])
        self.get_CHK(data[-2:0])
        
    def get_CMD(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        data = int(data, 2)
        if data <= 8:
            self.cmd = commandFrame.CMD_MSG[data]
        else:
            self.cmd = 'Undefined'
        return
    
    def get_EXTFRAME(self, data):
        self.extframe = ''.join(bin(byte)[2:].zfill(8) for byte in data)

if __name__ == "__main__":
    # data = b'\xaa\x01\x00^\x00\x01f\xd9\x97{\x07\x0b\xb2\xcb\x00\x00F\x1a\xcdQ:\x0b\xb6ZE"\xc8\x05\xbe\xc0K\x99Bp\x00\x01\x00\x00\x00\x00\x00\x00F%\xba\xf9>-\xf4eE\xa0\x14:>-\xf4ABp\x00\x01\x00\x00\x00\x00\x00\x00E\xff4\xf2=\x98-\x13EY\x08\x04=\xee\xa6=Bp\x00\x01\x00\x00\x00\x00\xc4<'
    # data = b'\xaa\x01\x00*\x00\x01f\xf4W\x05\x08\x08\xa5\x8b\x00\x00F\x1bgz>m\xf8yE\xa1\xbe8=&\x05|Bh\x97T\x00\x00\x00\x00Ex'
    # cfg = b'\xaa1\x00^\x00\x01f\xf1\xc0X\x00\x06\x1a\x80\x00\x0fB@\x00\x01GEN-        1- 1\x00\x01\x00\x0f\x00\x02\x00\x00\x00\x00Voltage         Current         \x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x1e\xc4\xc0'
    cfg = b'\xaa1\x00^\x00\x01g6>.\x00\x02\x8b\x0b\x00\x0fB@\x00\x01BUS-           7\x00\x01\x00\x0f\x00\x02\x00\x00\x00\x00Voltage         Current         \x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x1e\x0b\x0c'
    dnt = b'\xaa\x01\x00*\x00\x01g6>0\x08\x06\x9c\xb5\x00\x00H\x04\xfcL=\x93,\xf1\x00\x00\x00\x00\x00\x00\x00\x00Bp\x00\x00\x00\x00\x00\x00\x0f\x19'
    frame = cfg1(cfg)
    # print(frame)
    # print(frame)
    frame = dataFrame(data=dnt, pmuinfo=frame.pmus, time_base=frame.time_base, num_pmu=frame.num_pmu)
    print(frame)
    # print(frame.start)
# 10bits - 001000000001011010