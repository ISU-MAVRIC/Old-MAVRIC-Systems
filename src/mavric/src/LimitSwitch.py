#!/usr/bin/env python
# Applies limit switches to a value. If the switches are active, then the value is not passed outside of the set limits. 
#   E.g. If the low limit switch is active and the low limit is set to 0.0015, then the output will be the max(input, 0.0015)

# Parameters:
#   <low|high>_limit - the min/max value of the output when the low/high limit switches are active. i.e.
#   switch_<low|high>_active_low - T/F: True indicates that a falue of True from the switch means that it is innactive, false (default) trasts a value of True as active.
#   use_switch_<low|high> - False to ignore the switch, treating it as always inactive.

# Topics:
#   signal_input - Subscription: the control input from the user/controller
#   signal_output - Publication: Output from the limit switch application. If no switches are active, then the output follows the input.
#   switch_<low|high> - Subscription: The data from the switch, must be a boolean value, see PiGPIO_Input.py

import rospy
from std_msgs.msg import Float64
from std_msgs.msg import Bool

output_topic = None
signal_value = None
low_enabled = False
high_enabled = False
low_limit = None
high_limit = None
        
def update_output():
        if signal_value < low_limit and not low_enabled:
                to_output = low_limit
                print('low limit')
        elif signal_value > high_limit and not high_enabled:
                to_output = high_limit
                print('high limit')
        else:
                to_output = signal_value
        output_topic.publish(to_output)


def sig_callback(data):
        global signal_value
        signal_value = data.data
        update_output()
        
def switch_low_callback(data):
        global low_enabled
        adjusted = not(data.data)
        if low_enabled != adjusted:
                low_enabled = adjusted
                update_output()

def switch_high_callback(data):
        global high_enabled
        adjusted = not(data.data)
        if high_enabled != adjusted:
                high_enabled = adjusted
                update_output()


def talker():
        global low_limit
        global high_limit
        global output_topic
        global low_enabled
        global high_enabled
        
        rospy.init_node('LimitSwitch')
        output_topic = rospy.Publisher('signal_out', Float64, queue_size=10)

        low_limit = rospy.get_param('~low_limit', 0)
        high_limit = rospy.get_param('~high_limit', 0)

        use_switch_low = rospy.get_param('~use_switch_low', False)
        use_switch_high = rospy.get_param('~use_switch_high', False)
        low_enabled = not use_switch_low
        high_enabled = not use_switch_high
        print(low_enabled, high_enabled)
        if use_switch_low:
                rospy.Subscriber('switch_low', Bool, switch_low_callback, queue_size=10)
        if use_switch_high:
                rospy.Subscriber('switch_high', Bool, switch_high_callback, queue_size=10)

        rospy.Subscriber('signal_in', Float64, sig_callback, queue_size=10)

        rospy.spin()
        
if __name__ == '__main__':
    talker()
