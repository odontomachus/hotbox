import sys
import io
from collections import defaultdict
import struct
from time import sleep
import queue
import threading

import serial
from serial import SerialException

RUN_LABELS = ('Time left', 'Temp 1', 'Temp 2', 'Off Goal', 'Temp Change', 'Duty cycle (/30)', 'Heating', 'Cycle')

MSG_RUN_STATUS = 1
MSG_CONFIG = 2
MSG_STATUS = 3
MSG_LENGTHS = {MSG_RUN_STATUS: 13, MSG_CONFIG: 7, MSG_STATUS: 5}

STATE_START = 1
STATE_ACTIVE = 2
STATE_READY = 3
STATE_BOOT = 4
STATE_INIT = 5

class RunStatus:
    __slots__ = ('countdown', 't1', 't2', 'dg', 'dt', 'part', 'state', 'cycle')
    def __init__(self, message):
        self.t1 = message[0]
        self.t2 = message[1]
        self.countdown = message[2]*256 + message[3]
        self.part = message[4]
        self.cycle = message[5]
        self.state = "On" if message[6] != 0 else "Off"
        self.dg = struct.unpack('b', message[7:8])[0]
        self.dt = struct.unpack('b', message[8:9])[0]

    def __str__(self):
        return "\t".join(
            map(str,
                (self.countdown,
                 self.t1,
                 self.t2,
                 self.dg,
                 self.dt,
                 self.part,
                 self.state,
                 self.cycle,
             )
            ))

class OvenConfig:
    __slots__ = ('temp', 'time')
    def __init__(self, message):
        self.time = message[0]*256 + message[1]
        self.temp = message[2]

class OvenStatus:
    __slots__ = ('status',)
    def __init__(self, message):
        self.status = message[0]

class Client(threading.Thread):
    """ Client class for hotbox serial connection """
    parsers = {
        MSG_STATUS: OvenStatus,
        MSG_RUN_STATUS: RunStatus,
        MSG_CONFIG: OvenConfig,
    }

    def __init__(self):
        super().__init__()
        self.state = 'disconnected'
        self.msg_queue = {MSG_STATUS: queue.Queue(), 
                          MSG_CONFIG: queue.Queue(), 
                          MSG_RUN_STATUS: queue.Queue(),
                      }

    def connect(self, port):
        try:
            self.conn = serial.Serial(port, 9600, timeout=0.05)
            # empty buffer
            while len(self.conn.read(1)) > 0:
                pass

            self.state = 'connected'

            sleep(0.01)
            self.oven_query_config()

            sleep(0.2)
            self.oven_status()


        except SerialException:
            self.state = 'disconnected'
        finally:
            self.start_message = 0

    def run(self):
        self.running = 1

        parsed_length = 0
        mtype = 0
        msg_length = 0

        
        while self.running:

            # Don't do anything if disconnected
            if (self.state == 'disconnected'):
                sleep(0.1)
                continue

            try:
                c = self.conn.read(1)
            except SerialException:
                self.state = 'disconnected'
                sleep(0.1)
                continue

            # wait for message
            if not c:
                continue

            # this is the message type byte
            if parsed_length == 3:
                parsed_length += 1
                if c[0] == 0:
                    continue
                mtype = c[0]
                msg_length = MSG_LENGTHS[mtype]
                buffer = bytes()
                continue

            if parsed_length < 3:
                # Abort if not a null byte
                if c[0]:
                    parsed_length = 0
                    continue
                # otherwise increment parsed length
                parsed_length += 1
                continue

            # in any other case this is a data byte
            parsed_length += 1
            buffer += c
            if parsed_length == msg_length:
                data = self.parsers[mtype](buffer)
                self.msg_queue[mtype].put(data)
                parsed_length = 0
                mtype = 0
                msg_length = 0

    def oven_configure(self, ctime, temp):
        if self.state == "connected":
            self.conn.write(b'c'+struct.pack('B', ctime//256) + struct.pack('B', ctime%256) + struct.pack('B', temp))

    def oven_start(self):
        if self.state == "connected":
            self.conn.write(b's')

    def oven_stop(self):
        if self.state == "connected":
            self.conn.write(b't')

    def oven_status(self):
        if self.state == "connected":
            self.conn.write(b'r')

    def oven_query_config(self):
        if self.state == "connected":
            self.conn.write(b'q')
