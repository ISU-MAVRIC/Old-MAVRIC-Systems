#!/usr/bin/env python
# Monitors the input topic and publishes a 0,0 message if there are no updates for too long

# Parameters
#  ~timeout: Defines the length of time (in seconds) before the stop message is sent.
#              Longer times make it easier to test things in the lab.
#              Shorter times make the rover safer.

# Topics:
#   Drive_Train - Subscription: Monitors for activity on the topic
#   Drive_Train - Publication: Publishes a stop message when there is no activity

import rospy
from mavric.msg import Drivetrain

frame = 0


def callback(data):
    global frame
    frame = 0


def talker():
    global frame
    rospy.init_node('DrivetrainHartbeat')
    timeout = rospy.get_param('~timeout', 10)
    rospy.Subscriber('Drive_Train', Drivetrain, callback, queue_size=10)
    pub = rospy.Publisher('Drive_Train', Drivetrain, queue_size=10)
    frame = 0
    r = rospy.Rate(100/timeout)
    while not rospy.is_shutdown():
        r.sleep()
        frame = frame + 1
        if (frame > 100):
            print('timeout')
            pub.publish(0, 0, 0, 0, 0, 0)
            frame = 0


if __name__ == '__main__':
    talker()
