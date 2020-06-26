#!/usr/bin/python
# -*- coding: utf-8 -*-
import serial

class SerialPort:
    def __init__(self, port, buand):
        self.port = serial.Serial(port, buand, timeout=0.5)
        self.port.close()
        if not self.port.isOpen():
            self.port.open()

    def port_open(self):
        if not self.port.isOpen():
            self.port.open()

    def port_close(self):
        self.port.close()

    def send_data(self, data):
        self.port.write(data)

    def read_data(self):
        global is_exit
        global data_bytes
        while not is_exit:
            count = self.port.inWaiting()
            if count > 0:
                rec_str = self.port.read(count)
                data_bytes=data_bytes+rec_str
                #print('当前数据接收总字节数：'+str(len(data_bytes))+' 本次接收字节数：'+str(len(rec_str)))
                #print(str(datetime.now()),':',binascii.b2a_hex(rec_str))

def recv(serial):
    while True:
        data = serial.read_all()
        if data == '':
            continue
        else:
            break
        sleep(0.02)
    return data