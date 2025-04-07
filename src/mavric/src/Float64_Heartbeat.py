#!/usr/bin/env python
# Monitors the Drive_Train topic and publishes a 0,0 message if there are no updates for too long

# Parameters
#  ~timeout: Defines the length of time (in seconds) before the stop message is sent.
#              Longer times make it easier to test things in the lab.
#              Shorter times make the rover safer.

# Topics:
#   topic - Subscription: Monitors for activity on the topic
#   topic - Publication: Publishes a stop message when there is no activity

import rospy
from std_msgs.msg import Float64

frame = 0

def callback(data):
        global frame
        frame = 0

def talker():
        global frame
        rospy.init_node('Float64_Heartbeat')
        timeout = rospy.get_param('~timeout', 2)
        reset_val = rospy.get_param("~value", 0)
        rospy.Subscriber('topic', Float64, callback, queue_size=10)
        pub = rospy.Publisher('topic', Float64, queue_size=10)
        frame = 0
        r = rospy.Rate(10/timeout)
        while not rospy.is_shutdown():
                r.sleep()
                frame = frame + 1
                if (frame > 10):
                        print('timeout')
                        pub.publish(reset_val)
                        frame = 0

if __name__ == '__main__':
    talker()
