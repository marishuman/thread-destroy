import struct

# HDR
HDR = 0xA5A5

#TYPES
MAG_TYPE = b"mag:"

#PORTS
MOMENT_PORT = 10123

def unpackRadData(s):
    hdr = struct.unpack('<H', s[0:2])[0]
    ant = struct.unpack('<H', s[2:4])[0]
    azi = (360 * struct.unpack('<H', s[4:6])[0]/2**15 + ant * 90) % 360
    sec = struct.unpack('<I', s[8:12])[0]
    tic = struct.unpack('<I', s[12:16])[0]
    sps = struct.unpack('<I', s[16:20])[0]
    data = struct.unpack('<%df' % sps, s[24::]) 
    return [ant, azi, sec, tic, sps, data]