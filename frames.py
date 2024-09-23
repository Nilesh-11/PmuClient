from abc import ABCMeta

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
        self.frame_version = int(data[8:12])
        self.frame_type = int(data[12:15])
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
    Frame Version : {self.frame_version}
    Frame Type : {commonFrame.FRAME_TYPES_WORDS[self.frame_type]}
    Frame size : {self.framesize}
    Stream ID Code : {self.stream_idcode}
    SOC : {self.soc}
    Time quality : {self.msg_tq}
    FRACSEC : {self.fracsec}
    """

class pmu(object):
    
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
        self.get_PHNMR(data[start : start + 4])
        start += 4
        self.get_DGNMR(data[start : start + 2])
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
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.stn = int(data, 2)
        pass
    
    def get_Data_IDCODE(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.data_idcode = int(data, 2)
        pass
    
    def get_FORMAT(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.format = bin(data[0:4])[2:]
        pass
    
    def get_PHNMR(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.phnmr = int(data, 2)
        pass
    
    def get_ANNMR(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.annmr = int(data, 2)
        pass
    
    def get_DGNMR(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.dgnmr = int(data, 2)
        pass
    
    def get_CHNAM(self, data):
        # channel_name = ''.join(chr(b) if 32 <= b < 127 else f'\\x{b:02x}' for b in data)
        def parse(data):
            return data.decode('ascii', error='ignore')
        self.chnam = {
            "phasor": [],
            "analog": [],
            "digital": []
        }
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
            for i in range(16):
                phname = data[cur : cur + 16]
                dgnames.append(parse(phname))
                cur += 16
            self.chnam["digital"].append(parse(dgnames))
        return cur
    
    def get_PHUNIT(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        phasor_type = int(data[0:8], 2)
        scale = int(data[8:], 2)
        if phasor_type != 0:
            return scale, "i"
        else:
            return scale, "v"
    
    def get_ANUNIT(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        
        TYPES = { "0": "pow", "1": "rms", "2": "peak" }
        analog_type = int(data[0:8], 2)
        scale = int(data[8:], 2)
        
        return scale, TYPES[str(analog_type)]

    def get_DIGUNIT(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        digital_type = int(data[0:16], 2)
        scale = int(data[16:], 2)

        return scale, digital_type

    def get_FNOM(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        return data
    
    def get_CFGCNT(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        return int(data, 2)

class cfg1(commonFrame):
    def __init__(self, data):
        super().__init__(data[0:14])
        self.get_TIME_BASE(data[14:18])
        self.get_NUM_PMU(data[18:20])
        self.pmu = []
        start = 20
        for i in range(self.num_pmu):
            ipmu = pmu(start)
            start = ipmu.end
            self.pmu.append(ipmu)

        self.data_rate = self.get_DATA_RATE(data[start : start + 2])
        start += 2
        self.chk = self.get_CHK(data[start : start + 2])
        pass
    
    def get_TIME_BASE(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.time_base = int(data[0:24], 2)
        pass
    
    def get_NUM_PMU(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.num_pmu = int(data, 2)
        pass
    
    def get_DATA_RATE(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        return int(data, 2)
    

class dataFrame(commonFrame):
    
    def __init__(self, data, time_base=1000000, num_pmu=1, format=b'0000', phnmr=1, annmr=1, dgnmr=1):
        '''
        data = byte (0, 1, 2 ... bit)
        '''
        super().__init__(data[0:14])
        
        self.time_base = time_base
        self.num_pmu = num_pmu
        self.format = format
        self.phnmr = phnmr
        self.annmr = annmr
        self.dgnmr = dgnmr
        self.pmu_data = []
        self.pmu_data_len = 2 + (4 if self.format[1] == 0 else 8) * self.phnmr + (2 if format[3] == 0 else 4) * 2 + (2 if format[3] == 0 else 4) * self.annmr + 2 * self.dgnmr
        
        for i in range(num_pmu):
            left = i * self.pmu_data_len + 14
            right = i * self.pmu_data_len + 16
            self.get_STAT(data[left : right])
            
            left = right
            right += (4 if self.format[1] == 0 else 8) * self.phnmr
            self.get_PHASORS(data[left : right])
            
            left = right
            right += (2 if format[3] == 0 else 4)
            self.get_FREQ(data[left : right])
            
            left = right
            right += (2 if format[3] == 0 else 4)
            self.get_DFREQ(data[left : right])
            
            left = right
            right += (2 if format[3] == 0 else 4) * self.annmr
            self.get_ANALOG(data[left : right])

            left = right
            right += 2 * self.dgnmr
            self.get_DIGITAL(data[left : right])
            
            self.save_pmu_data()
            
        self.get_CHK(data[-2:])
        print(self.pmu_data)
        pass
    
    def get_STAT(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.data_error = int(data[14:16], 2)
        self.trigger_reason = int(data[0:4], 2)
        self.PMU_sync = int(data[13], 2)
        return
    
    
    def get_PHASORS(self, data):
        self.phasors = []
        for i in range(self.phnmr):
            start = i * (4 if self.format[1] == 0 else 8)
            end = start + (4 if self.format[1] == 0 else 8)
            self.phasors.append(int(''.join(bin(byte)[2:].zfill(8) for byte in data[start : end]), 2))
        pass
    
    def get_FREQ(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.freq = int(data, 2)
        pass

    def get_DFREQ(self, data):
        data = ''.join(bin(byte)[2:].zfill(8) for byte in data)
        self.rocof = int(data, 2)
        pass
    
    def get_ANALOG(self, data):
        self.analog = []
        for i in range(self.annmr):
            start = i * (4 if self.format[2] == 0 else 8)
            end = start + (4 if self.format[2] == 0 else 8)
            self.analog.append(int(''.join(bin(byte)[2:].zfill(8) for byte in data[start : end]), 2))
        pass
    
    def get_DIGITAL(self, data):
        self.digital = []
        for i in range(self.dgnmr):
            start = i * 2
            end = start + 2
            self.digital.append(int(''.join(bin(byte)[2:].zfill(8) for byte in data[start : end]), 2))
        pass
    
    def save_pmu_data(self):
        data = {
            "STAT" : {
                "Data Error" : self.data_error,
                "Trigger Reason" : self.trigger_reason,
                "PMU Sync" : self.PMU_sync
            },
            "PHASORS" : self.phasors,
            "ANALOG" : self.analog,
            "FREQ" : self.freq,
            "ROCOF" : self.rocof,
            "DIGITAL" : self.digital
        }
        self.pmu_data.append(data)
        pass
    
    def __str__(self):
        return f"""\
    Frame Version : {self.frame_version}
    Frame Type : {commonFrame.FRAME_TYPES_WORDS[self.frame_type]}
    Frame size : {self.framesize}
    ID Code : {self.stream_idcode}
    SOC : {self.soc}
    Time quality : {self.msg_tq}
    FRACSEC : {self.fracsec}
    Data Error : {bin(self.data_error)[2:]}
    PMU sync : {self.PMU_sync}
    Trigger reason : {self.trigger_reason}
    
    """

class headerFrame(object):
    
    def __init__(self, data):
        pass

if __name__ == "__main__":
    data = b'\xaa\x01\x00^\x00\x01f\xd9\x97{\x07\x0b\xb2\xcb\x00\x00F\x1a\xcdQ:\x0b\xb6ZE"\xc8\x05\xbe\xc0K\x99Bp\x00\x01\x00\x00\x00\x00\x00\x00F%\xba\xf9>-\xf4eE\xa0\x14:>-\xf4ABp\x00\x01\x00\x00\x00\x00\x00\x00E\xff4\xf2=\x98-\x13EY\x08\x04=\xee\xa6=Bp\x00\x01\x00\x00\x00\x00\xc4<'
    frame = dataFrame(data)
    print(frame)
# 10bits - 001000000001011010