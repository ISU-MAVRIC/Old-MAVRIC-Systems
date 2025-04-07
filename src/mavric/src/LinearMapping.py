#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64
from std_msgs.msg import Bool


def callback(data, args):
    global lowLimit, highLimit
    pub = args[0]
    dat = data.data
    if dat > highLimit:
        dat = highLimit
    if dat < lowLimit:
        dat = lowLimit
    pub.publish(dat*args[1]+args[2])


def talker():
    global lowLimit, highLimit
    global slope
    global intercept

    rospy.init_node('LinearMapping')
    inputs = rospy.get_param('~inputs', 'q')
    outputs = rospy.get_param('~outputs', 'q')

    slopes = rospy.get_param('~slopes', '0')
    # MODES:
    # 0: normal operation (-100 to 100)
    # 1: claw operation
    lowLimit = rospy.get_param("~lowLimit", 100)
    highLimit = rospy.get_param("~highLimit", 100)
    if type(slopes) == str:
        slopes = float(slopes)
    else:
        slopes = slopes

    intercepts = rospy.get_param('~intercepts', '0')
    if type(intercepts) == str:
        intercepts = float(intercepts)
    else:
        intercepts = intercepts

    #if len(inputs) != len(outputs):
        #raise ValueError("The inputs and outputs are not the same size")
    #if len(inputs) != len(slopes):
        #raise ValueError("The inputs and slopes are not the same size")
    #if len(inputs) != len(intercepts):
        #raise ValueError("The inputs and intercepts are not the same size")

    output_topic = rospy.Subscriber(inputs, Float64, callback, (rospy.Publisher(
            outputs, Float64, queue_size=10), slopes, intercepts), queue_size=10)

    rospy.spin()


if __name__ == '__main__':
    talker()
