#!/usr/bin/env python3
import time
import serial
import adafruit_gps
import rospy

from mavric.msg import GPS as GPS_MSG
from std_msgs.msg import Bool as BOOL_MSG

# setup code for gps
uart = serial.Serial('/dev/ttyTHS2', baudrate=9600, timeout=10)  # create serial connection through serial port J17
gps = adafruit_gps.GPS(uart, debug=False)  # Create GPS instance
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")  # Turn on the basic GGA and RMC info
gps.send_command(b"PMTK220,1000")  # Set update rate to once a second (1hz)


# talker function
def talker():
    rospy.init_node('GPS_Streamer')
    pub = rospy.Publisher('GPS_Data', GPS_MSG, queue_size=10, latch=True)
    pub_gps_fix = rospy.Publisher('GPS_Fix', BOOL_MSG, queue_size=10, latch=True)
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        gps.update()
        if not gps.has_fix:
            pub_gps_fix.publish(False)
        else:
            pub_gps_fix.publish(True)
            h = gps.timestamp_utc.tm_hour
            m = gps.timestamp_utc.tm_min
            s = gps.timestamp_utc.tm_sec
            pub.publish(gps.latitude, gps.longitude, gps.altitude_m, gps.speed_knots, gps.track_angle_deg, gps.satellites, h, m, s)
        rate.sleep()


# main loop
if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
