#!/usr/bin/env python

import sys, os
import time

from pymavlink import pixhawk as mavlink
from BPlus import DataManagerInterface
from connection import SimpleMAV

class fifo(object):
    def __init__(self):
        self.buf = []
    def write(self, data):
        self.buf += data
        return len(data)
    def read(self):
        return self.buf.pop(0)

def create_vector_from_pixhawk(message):
    data_vector = []
    if message is None:
        return data_vector
    for field_name in message.get_fieldnames():
        data_vector.append(message.__getattribute__(field_name))
    return data_vector

if __name__ == "__main__":
    # we will use a fifo as an encode/decode buffer
    f = fifo()
    # create a mavlink instance, which will do IO on file object 'f'
    mav = mavlink.MAVLink(f)
    B = DataManagerInterface()
    pixhawk = SimpleMAV(master="/dev/ttyACM0")


    for i in range (0,100):
        msg = pixhawk.conn.recv_msg()
        print msg

    for i in range (0,100):
        msg = pixhawk.conn.recv_msg()
        if msg is None:
            continue
        msg_vector = create_vector_from_pixhawk(msg)
        if 0 < msg.get_msgId() < 900:
            B.insertMeasurement(msg.get_msgId(), msg_vector, time.time())
        time.sleep(0.01)
    # get messages
    estim = B.estimate(27, time.time()-2)
    print estim




    # cases... m.get_type()
    # m = mav.raw_imu_encode(475496833,38,-18,-995,14,59,0,84,-109,288)
    # B.insertMeasurement(m.get_msgId(), create_vector_from_pixhawk(m), time.time()) #TODO timestamp switch
    # time.sleep(3)
    # m = mav.raw_imu_encode(475496700,42,-18,-999,20,200,0,80,-100,281)
    # B.insertMeasurement(m.get_msgId(), create_vector_from_pixhawk(m), time.time())
    #
    # estim = B.estimate(m.get_msgId(), time.time()-2)
    # print estim

    # decode an incoming message
    # m2 = mav.decode(b)

    # show what fields it has
    # print("Got a message with id %u and fields %s" % (m2.get_msgId(), m2.get_fieldnames()))

    # print out the fields
    # print(m2)
