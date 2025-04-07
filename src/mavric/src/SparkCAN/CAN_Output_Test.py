import can
from time import time, sleep
from struct import *
import math

from SparkCAN import SparkBus
import time

#Instantiate SparkBus object
bus = SparkBus(channel="can0", bustype='socketcan', bitrate=1000000)
#Create a new controller with CAN id 1
for i in range(1, 7):
    sparkESC = bus.init_controller(i)
    time.sleep(1)
    #Set motor to 50% power
    sparkESC.percent_output(.2) #50%
    #Prints the velocity 10 times, you should be able to see it ramp up as the motor gets up to speed.
    for i in range(10):
        print(sparkESC.velocity)
        time.sleep(0.001)
    #wait 5 seconds
    time.sleep(5)
    #Set motor to 0% power
    sparkESC.percent_output(0)

"""
bus = can.interface.Bus('can0', bustype='socketcan', bitrate=1000000)


def can_send(msg):
    try:
        bus.send(msg)
        #print("Message sent on {}".format(bus.channel_info))
    except can.CanError:
        print("Message not sent")


def send_heartbeat():
    msg = can.Message(arbitration_id=0x02052480,
            data=[0x06, 0, 0, 0, 0, 0, 0, 0])  # mask enabling ids 1 + 2 ...  0x0e enables ids 1,2, and 3
    can_send(msg)


def packer_float(value):
    hexStr = pack('fi', value, 0)
    return hexStr


def set_percent_output(id, value):
    msg = can.Message(arbitration_id= 0x02050080 + id, data=packer_float(value))
    can_send(msg)


def set_velocity_output(id, value):
    msg = can.Message(arbitration_id= 0x02050480 + id, data=packer_float(value))
    can_send(msg)


#while True:
 #   send_heartbeat()
#    set_percent_output(2, math.sin(time()*0.25))
#    sleep(0.002)


while True:
    send_heartbeat()
    set_velocity_output(3, 10)
    print('a')
    sleep(0.02)
"""