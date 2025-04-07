#!/usr/bin/env python
# Ramping node, listens to messages on the input topic
#   and applies a maximum ramp rate.

# Paremeters:
#   ~update_rate - How often the output topic is updated while ramping is active in Hz.
#   ~ramp_rate_up - the rate the control signal accelerates in hz
#   ~ramp_rate_down - the rate the control signal deccelerates in hz
#   ~centerpoint - the value where the controller witches from ramping up and ramping down.

# Topics:
#   input - Subscription: the setpoint value,
#     as time approaches infinity without a change in input,
#     the output will match the input.
#   output - Publication: the output value. The output will not change faster than the given ramp rates and will update at the update_rate when changing.

import rospy
from std_msgs.msg import Float64
import time

def callback(data):
        global target
        target  = data.data


def rampVal(current, target, centerpoint, ramp_amount_up, ramp_amount_down):
        if (current == target):
                return current;
        if current >= centerpoint and target > centerpoint:
                if current < target:
                        current = current + min(ramp_amount_up, target-current)
                else:
                        current = current - min(ramp_amount_down, current-target)
        elif current > centerpoint and target <= centerpoint:
                current = current - min(ramp_amount_down, current-target)
        elif current <= centerpoint and target < centerpoint:
                if current > target:
                        current = current - min(ramp_amount_up, current-target)
                else:
                        current = current + min(ramp_amount_down, target-current)
        elif current < centerpoint and target >= centerpoint:
                current = current + min(ramp_amount_down, target-current)
        else:
                print("case missed" + str(current) + "->" + str(target))
                current = target;
        return current
        
def listener():
        global target
        rospy.init_node('Ramping')
        rospy.Subscriber("input", Float64, callback, queue_size=10)
        pub = rospy.Publisher("output", Float64, queue_size=10)

        rate = rospy.get_param("~update_rate", 10)
        ramp_rate_up = rospy.get_param("~ramp_rate_up", 0.5)/rate
        centerpoint = rospy.get_param("~centerpoint", 0)
        ramp_rate_down = rospy.get_param("~ramp_rate_down", 0.5)/rate

        r = rospy.Rate(rate)
        value = 0;
        target = 0
        while not rospy.is_shutdown():
                if (value != target):
                        value = rampVal(value, target, centerpoint, ramp_rate_up, ramp_rate_down)
                        pub.publish(value);        
                r.sleep()
                
if __name__ == '__main__':
    listener()
