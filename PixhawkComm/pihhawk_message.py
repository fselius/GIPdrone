#!/usr/bin/env python

import sys, os

from pymavlink import pixhawk as mavlink
from BPlus import DataManagerInterface

class fifo(object):
    def __init__(self):
        self.buf = []
    def write(self, data):
        self.buf += data
        return len(data)
    def read(self):
        return self.buf.pop(0)

# we will use a fifo as an encode/decode buffer
f = fifo()

# create a mavlink instance, which will do IO on file object 'f'
mav = mavlink.MAVLink(f)

# set the WP_RADIUS parameter on the MAV at the end of the link
# mav.param_set_send(7, 1, "WP_RADIUS", 101, mavlink.MAV_PARAM_TYPE_REAL32)

# alternatively, produce a MAVLink_param_set object
# this can be sent via your own transport if you like
# m = mav.param_set_encode(7, 1, "WP_RADIUS", 101, mavlink.MAV_PARAM_TYPE_REAL32)
m = mav.raw_imu_encode(475496833,38,-18,-995,14,59,0,84,-109,288)


# print fields
print(m)

# get the encoded message as a buffer
b = m.get_msgbuf()
for field_name in m.get_fieldnames():
    print(field_name, m.__getattribute__(field_name))

B = DataManagerInterface()
print(m.get_type())
B.insertMeasurement(m.get_msgId(),m.xacc,100)
B.insertMeasurement(m.get_msgId(),m.xacc + 10, 200)
fail_res = B.estimate(m.get_msgId(), 150)
print fail_res

# decode an incoming message
# m2 = mav.decode(b)

# show what fields it has
# print("Got a message with id %u and fields %s" % (m2.get_msgId(), m2.get_fieldnames()))

# print out the fields
# print(m2)
