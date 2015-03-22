from collections import defaultdict
import struct

import serial
from serial import SerialException

PORT="/dev/ttyUSB0"

s = serial.Serial(PORT, 9600, timeout=0.5)

keys = ['Time left', 'T1', 'T2', 'Off goal', 'Temp diff', 'Part', 'State', 'Cycle']

def listen():
    print("\t".join(keys))
    while True:
        try:
            message = s.read(30)
            row = defaultdict(str)
            parse_message(message, row)
            if row:
                    print("\t".join(map(lambda key: str(row[key]), keys)))
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
                

# empty buffer
while len(s.read(1)) > 0:
    pass

d = {}

s.write(b's')
listen()

