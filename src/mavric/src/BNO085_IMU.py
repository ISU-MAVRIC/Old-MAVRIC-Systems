#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float64
from geometry_msgs.msg import Vector3
from adafruit_bno08x.i2c import BNO08X_I2C
import adafruit_bno08x as BNO08X
from scipy.spatial.transform import Rotation
import board

i2c = board.I2C()
bno = BNO08X_I2C(i2c)
bno.enable_feature(BNO08X.BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO08X.BNO_REPORT_MAGNETOMETER)
bno.enable_feature(BNO08X.BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR)

calibration_enabled = False

def talker():
    global calibration_enabled
    rospy.init_node('BNO085_IMU')
    pub_sys_cal = rospy.Publisher("IMU/SysCalibration", Float64, queue_size=10)
    pub_angle = rospy.Publisher("IMU/FusedAngle", Vector3, queue_size=10)
    rate = rospy.Rate(10)

    calibration_enabled = rospy.get_param('~calibration_enabled', False)
    if calibration_enabled:
        bno.begin_calibration()
        rospy.loginfo("Calibration Started")


    while not rospy.is_shutdown():
        mag_quat = bno.geomagnetic_quaternion
        rot = Rotation.from_quat(mag_quat)
        pitch, roll, yaw = rot.as_euler('xyz', degrees=True)
        
        sys_cal = bno.calibration_status
        yaw = -yaw
        if yaw < 0:
            yaw = 360 + yaw
        pub_sys_cal.publish(sys_cal)
        pub_angle.publish(roll, pitch, yaw)

        rate.sleep()


if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        if calibration_enabled:
            bno.save_calibration_data()
            rospy.loginfo("Calibration Saved")
        pass