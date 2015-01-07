import atexit
import sys
import time
import os
import numpy
import signal
import logging
import threading

from pymavlink import mavutil

def detect_pixhawk():
    '''
    Detect the serial port where pixhawk is connected automatically. Adapted from Mavproxy code.
    '''
    serial_list = mavutil.auto_detect_serial(preferred_list=['*FTDI*',"*Arduino_Mega_2560*", "*3D_Robotics*", "*USB_to_UART*"])
    if len(serial_list) == 1:
        return serial_list[0].device
    else:
        print('''
Please choose a MAVLink master with --master
For example:
        --master=com14
        --master=/dev/ttyUSB0
        --master=127.0.0.1:14550

Auto-detected serial ports are:
''')
        for port in serial_list:
            print("%s" % port)
            sys.exit(1)


class SimpleMAV(object):
    manual_control_string = "rc"

    def __init__(self, master, sysID=1, compoID=250):
        if master == "/dev/ttyACM0":
            master = detect_pixhawk()
            print "Pixhawk Master is", master
            baud = 115200
            reboot = False
        else:
            baud = 57600
            reboot = True

        self.conn = mavutil.mavlink_connection(device=master, baud=baud,
                                               autoreconnect=True)

