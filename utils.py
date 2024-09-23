def access_bit(data, byte, bit):
    byte_value = data[byte]
    return (byte_value>>bit)&1

def access_bits(data, lpos, rpos):
    '''
    lpos and rpos are bit position
    '''
    assert lpos < rpos, "incorrect bit position range"
    l = lpos // 4
    r = rpos // 4
    lpos = lpos % 4
    rpos = rpos % 4
    lbyte = data[l]
    rbyte = data[r]
    lbyte[l:4]
    lbyte[l:4]
    pass