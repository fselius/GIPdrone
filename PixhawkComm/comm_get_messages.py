from pymavlink import mavutil
from BPlus import DataManagerInterface
import time

def create_vector_from_pixhawk(message):
    data_vector = []
    if message is None:
        return data_vector
    for field_name in message.get_fieldnames():
        data_vector.append(message.__getattribute__(field_name))
    return data_vector

def detect_pixhawk():
    serial_list = mavutil.auto_detect_serial(preferred_list=['*FTDI*',"*Arduino_Mega_2560*", "*3D_Robotics*", "*USB_to_UART*"])
    return serial_list[0].device

class SimpleMAV(object):
    def __init__(self, master, sysID=1, compoID=250):
        master = detect_pixhawk()
        self.conn = mavutil.mavlink_connection(device=master, baud=115200, autoreconnect=True)

if __name__ == "__main__":
    s = SimpleMAV(master="/dev/ttyACM0")
    # time.sleep(1)
    # while not s.conn.motors_armed():
    #     s.conn.arducopter_arm()
    #     time.sleep(1.0)
    # time.sleep(1.0)
    s.conn.wait_heartbeat()
    B = DataManagerInterface()
    while 1:
        msg = s.conn.recv_msg()
        print"####################################"
        print msg