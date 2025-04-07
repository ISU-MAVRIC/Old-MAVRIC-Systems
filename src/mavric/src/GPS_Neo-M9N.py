#!/usr/bin/env python3

import rospy, serial
from mavric.msg import GPS
from std_msgs.msg import Bool
from ublox_gps import UbloxGps

# https://github.com/sparkfun/Qwiic_Ublox_Gps_Py/tree/master/examples

def talker():
    rospy.init_node("GPS_Streamer")
    gps_pub = rospy.Publisher("GPS_Data", GPS, queue_size=10, latch=True)
    fix_pub = rospy.Publisher("GPS_Fix", Bool, queue_size=10, latch=True)
    rate = rospy.Rate(1)

    port = serial.Serial('/dev/ttyACM0', baudrate=38400, timeout=10)
    gps = UbloxGps(port)

    while not rospy.is_shutdown():
        try:
            geo = gps.geo_coords()
            time = gps.date_time()
            nums = GPS()
            nums.latitude = geo.lat
            nums.longitude = geo.lon
            nums.altitude = geo.height
            nums.speed = geo.gSpeed
            nums.heading = geo.headMot
            nums.num_satellites = geo.numSV
            nums.time_h = int(time.hour)
            nums.time_m = int(time.min)
            nums.time_s = float(time.sec)
            if geo.flags.gnssFixOK == 0:
                fix_pub.publish(False)
            else:
                fix_pub.publish(True)
            gps_pub.publish(nums)

        except (ValueError, IOError) as err:
            print(err)
        rate.sleep()
    port.close()


if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        
        pass