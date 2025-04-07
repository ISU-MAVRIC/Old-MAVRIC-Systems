#!/usr/bin/env python3

import rospy
import time
from std_msgs.msg import Float64
from mavric.msg import ArmData,ScaleFeedback

arm_values = ArmData()
drive_value = Float64()

def drive_cb(data):
    global drive_value
    drive_value = data.data

def arm_cb(data):
    global arm_values
    arm_values = data

def talker():
    global drive_value, arm_values
    rospy.init_node("Scale_Manager")
    drive_sens = rospy.Publisher("Drive/Drive_Sensitivity", Float64, queue_size=10)
    arm_sens = rospy.Publisher("Arm/Arm_Sensitivity", ArmData, queue_size=10)
    feedback = rospy.Publisher("SensFeedback", ScaleFeedback, queue_size=10)
    drive_sub = rospy.Subscriber("Drive/Drive_Sensitivity", Float64, drive_cb, queue_size=10)
    arm_sub = rospy.Subscriber("Arm/Arm_Sensitivity", ArmData, arm_cb, queue_size=10)
    arm_values.ShoulderRot = rospy.get_param('~ShoulderRot', 1.0)
    arm_values.ShoulderPitch = rospy.get_param('~ShoulderPitch', 1.0)
    arm_values.ElbowPitch = rospy.get_param('~ElbowPitch', 1.0)
    arm_values.WristPitch = rospy.get_param('~WristPitch', 1.0)
    arm_values.WristRot = rospy.get_param('~WristRot', 1.0)
    drive_value = rospy.get_param('~Drive_Sens',1.0)
    time.sleep(5)
    drive_sens.publish(drive_value)
    arm_sens.publish(arm_values)
    rate = rospy.Rate(0.2)
    while not rospy.is_shutdown():
        values = ScaleFeedback()
        values.Drive = drive_value
        values.ShoulderPitch = arm_values.ShoulderPitch
        values.ShoulderRot = arm_values.ShoulderRot
        values.ElbowPitch = arm_values.ElbowPitch
        values.WristRot = arm_values.WristPitch
        values.WristPitch = arm_values.WristPitch
        feedback.publish(values)
        rate.sleep()


if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
