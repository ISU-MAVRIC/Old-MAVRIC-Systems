#!/usr/bin/env python
import rospy
import time
import os
from std_msgs.msg import Int32, String
from pySerialTransfer import pySerialTransfer as txfer
import driveMath


from mavric.msg import Drivetrain
from mavric.msg import Steertrain

port = '/dev/ttyACM1'

# Defaults and beginning values
drive = 0.0
steer = 0.0
mode = 0
parameters = [0,0,0,0,0,0,0,0,0,0]
deadzone = 0.05
sensitivity = 0.5
LoRaEnabled = False

class struct(object):
    drive = float
    steer = float
    mode = float


# Client Callback function that will run whenever the value for clients connected changes. 
# if connected clients is greater than zero, publish all zeros once and stop publishing to 
# stop interrupting websocket clients.
def client_cb(data):
    global LoRaEnabled
    val = int(data.data)
    if val == 0:
        LoRaEnabled = True
    else:
        if LoRaEnabled == True:
            drive.publish(0.0,0.0,0.0,0.0,0.0,0.0)
            steer.publish(0.0,0.0,0.0,0.0)
        LoRaEnabled = False


if __name__=='__main__':
    try:
        # Publishers and Subscribers
        drive = rospy.Publisher("/Drive/Drive_Command", Drivetrain, queue_size=10)
        steer = rospy.Publisher("/Drive/Steer_Command", Steertrain, queue_size=10)
        clients = rospy.Subscriber("client_count", Int32, client_cb, queue_size=10)
        rospy.init_node("LoRa_Radio")

        dataRX = struct
        link = txfer.SerialTransfer(port)   # setup serial transfer on port specified
        link.open() # open link between rover and LoRa

        while not rospy.is_shutdown():
            print("Starting Loop")
            if link.available():    # Recieve new data from serial
                print("Data Recieved")
                recSize = 0

                dataRX.drive = link.rx_obj(obj_type='f', start_pos=recSize)
                recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

                dataRX.steer = link.rx_obj(obj_type='f', start_pos=recSize)
                recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

                dataRX.mode = link.rx_obj(obj_type='f', start_pos=recSize)
                recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

                #print('drive: {}  steer: {}   mode: {}'.format(dataRX.drive, dataRX.steer, dataRX.mode)) # debug print
                print("Data converted")

                if LoRaEnabled:
                    # Round data and test against deadzone
                    dataRX.drive = 100*round(dataRX.drive, 2)
                    dataRX.steer = 100*round(dataRX.steer, 2)
                    if abs(dataRX.drive) < deadzone:
                        dataRX.drive = 0
                    if abs(dataRX.steer) < deadzone:
                        dataRX.steer = 0

                    # Drive Modes given mode switch's setting
                    # Had to use floats to compare since the mode can't be transfered in an int.
                    if dataRX.mode < 0.5:
                        parameters = driveMath.car_drive(dataRX.drive*sensitivity,dataRX.steer)
                    elif dataRX.mode > 0.5:
                        parameters = driveMath.point_drive(dataRX.drive,dataRX.steer*sensitivity)

                    #print("Drive: {}    Steer: {}".format(dataRX.drive,dataRX.steer)) # Test print statement
                    drive.publish(float(parameters[0]), float(parameters[1]), float(parameters[2]), float(parameters[3]), float(parameters[4]), float(parameters[5]))
                    steer.publish(float(parameters[6]), float(parameters[7]), float(parameters[8]), float(parameters[9]))
                    print("Publishing New Values")
            elif link.status < 0:   # Error codes for Serial Transfer Library 
                print("No Message Recieved")
                if link.status == txfer.CRC_ERROR:
                    print('ERROR: CRC_ERROR')
                elif link.status == txfer.PAYLOAD_ERROR:
                    print('ERROR: PAYLOAD_ERROR')
                elif link.status == txfer.STOP_BYTE_ERROR:
                    print('ERROR: STOP_BYTE_ERROR')
                else:
                    print('ERROR: {}'.format(link.status))
                drive.publish(0,0,0,0,0,0)
                steer.publish(0,0,0,0)
    except rospy.ROSInterruptException:
        print("Ros Interrupt")
        link.close()    # Close serial connection
        pass
