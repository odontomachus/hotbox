from collections import defaultdict
import struct
from time import sleep

import serial
from serial import SerialException

PORT="COM4"

def listen(s):
    keys = ['Time left', 'T1', 'T2', 'Off goal', 'Temp diff', 'Part', 'State', 'Cycle']
    print("\t".join(keys))
    out = open("hotbox.tsv")
    while True:
        try:
            message = s.read(100)
            if len(message) == 0:
                continue
            if message[0:4] != b"MSG:":
                try:
                    print(message.decode('ascii'))
                    sleep(0.2)
                except UnicodeDecodeError:
                    pass
            else:
                row = defaultdict(str)
                parse_message(message, row)
                if row:
                    print("\t".join(map(lambda key: str(row[key]), keys)))
                    out.write("\t".join(map(lambda key: str(row[key]), keys))+"\r\n")
                    out.flush()
        except SerialException as e:
            pass
        except KeyboardInterrupt:
            break



def parse_message(message, data):
    while len(message) > 4 and message[0:4] != b"MSG:":
        message = message[1:]
    if len(message) == 0:
        return False
    message = message[4:]
    while len(message) > 0:
        try:
            if message[0] == b'T'[0]:
                data['T1'] = message[1]
                data['T2'] = message[2]
                message = message[3:]
            elif message[0] == b'C'[0]:
                data['Time left'] = message[1]*256
                data['Time left'] += message[2]
                message = message[3:]
            elif message[0] == b'P'[0]:
                data['Part'] = message[1]
                message = message[2:]
            elif message[0] == b'Y'[0]:
                data['Cycle'] = message[1]
                message = message[2:]
            elif message[0] == b'S'[0]:
                data['State'] = "On" if message[1] != '\x00' else "Off"
                message = message[2:]
            elif message[0] == b'G'[0]:
                data['Off goal'] = struct.unpack('b', message[1:2])[0]
                message = message[2:]
            elif message[0] == b'D'[0]:
                data['Temp diff'] = struct.unpack('b', message[1:2])[0]
                message = message[2:]
            elif message == b":EOM":
                return True
            else:
                return False
        except:
            return False
                

def configure(s, ctime, temp):
    s.write(b'c'+struct.pack('B', ctime//256) + struct.pack('B', ctime%256) + struct.pack('B', temp))

s = serial.Serial(PORT, 9600, timeout=0.5)

# empty buffer
while len(s.read(1)) > 0:
    pass

# Set time and temperature
s.write(b't')
configure(s, 3600*6, 53)
s.write(b's')
listen(s)

