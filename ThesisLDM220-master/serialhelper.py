from Constants import *
import serial
import time
import error


def create_serial_connection(port):
    return serial.Serial(port, baudrate=38400, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE,
                         bytesize=serial.EIGHTBITS, rtscts=True, dsrdtr=True, timeout=0.1)


def writer(ser, string, timeout=CURRENTTIMEOUT):
    ser.write(string)
    now = time.time()
    text = b""
    while time.time()-now < timeout:
        text += ser.read()
    if text:
        if b'\n010F0037\r' not in text:
            return text
    raise error.DosimeterNotFound
