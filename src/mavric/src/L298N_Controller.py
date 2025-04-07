#!/usr/bin/env python3

#import libraries
import rospy
import RPi.GPIO as GPIO

from std_msgs.msg import Float64
from std_msgs.msg import Bool

GPIO.setmode(GPIO.BOARD)


def callback(data, args):
    global forward_pin
    global backward_pin
    if data.data < 0:
        GPIO.output(backward_pin, True)
        GPIO.output(forward_pin, False)
    elif data.data > 0:
        GPIO.output(backward_pin, False)
        GPIO.output(forward_pin, True)
    else:
        GPIO.output(backward_pin, False)
        GPIO.output(forward_pin, False)
    
    args[0].publish(abs(data.data)*args[1]+args[2])

def talker():
    global low_limit
    global slope
    global intercept
    global forward_pin
    global backward_pin
    
    rospy.init_node('LinearMapping')
    slope = rospy.get_param('~slope', 0)
    intercept = rospy.get_param('~intercept', 0)
    inputs = rospy.get_param('~input', 'in')
    outputs = rospy.get_param('~output', 'out')
    forward_pin = rospy.get_param('~forward', 26)
    backward_pin = rospy.get_param('~backward', 23)

    GPIO.setup(forward_pin, GPIO.OUT)
    GPIO.setup(backward_pin, GPIO.OUT)

    output_topic = rospy.Subscriber(inputs, Float64, callback, (rospy.Publisher(outputs, Float64, queue_size=10), slope, intercept), queue_size=10)

    rospy.spin()

if __name__ == '__main__':
    talker()
