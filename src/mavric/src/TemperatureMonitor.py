#!/usr/bin/env python
# Reads the CPU temperature. Does not work on WSL for Windows 10.

# Topics:
#   Temperature - Publication: Publishes the CPU temperature at a rate of about 10 Hz.

import rospy
from std_msgs.msg import Float64

def talker():

        rospy.init_node('TempMonitoring')
        pub = rospy.Publisher("Temperature", Float64, queue_size=10)
        r = rospy.Rate(10);
        while not rospy.is_shutdown():
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as content_file:
                        tempString = content_file.read()
                pub.publish(float(tempString)/1000)
                r.sleep()
        

if __name__ == '__main__':
    talker()
