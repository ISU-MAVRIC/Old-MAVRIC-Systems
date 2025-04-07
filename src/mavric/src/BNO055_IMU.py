#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float64
from geometry_msgs.msg import Vector3
import adafruit_bno055 as BNO055
import board

i2c = board.I2C()
bno = BNO055.BNO055_I2C(i2c)

pwm_offset_ms = 0
HEADING_OFFSET = 0


def angle_to_ms(angle):
    # convert from (-90 to 90) to about (1ms to 2ms)
    percent = (angle / 180.0) + 0.5
    return ((1 + percent) * 0.001) + (pwm_offset_ms * 0.001)


def servo_cal_roll(pub):
    # allow IMU to auto-calibrate roll angle
    pub.publish(angle_to_ms(-60))
    rospy.sleep(0.5)

    pub.publish(angle_to_ms(60))
    rospy.sleep(0.5)

    pub.publish(angle_to_ms(0))
    rospy.sleep(0.5)


def talker():
    global pwm_offset_ms
    cal = True

    # define custom 3-variable message type for this
    pub_sys_cal = rospy.Publisher("IMU/SysCalibration", Float64, queue_size=10)
    pub_cal = rospy.Publisher("IMU/SensorCalibrations", Vector3, queue_size=10)

    pub_angle = rospy.Publisher("IMU/FusedAngle", Vector3, queue_size=10)

    #pub_gyro_raw = rospy.Publisher("IMU/RawGyro", Vector3, queue_size=10)
    #pub_accel_raw = rospy.Publisher("IMU/RawAccel", Vector3, queue_size=10)
    #pub_mag_raw = rospy.Publisher("IMU/RawMag", Vector3, queue_size=10)

    pub_servo = rospy.Publisher("IMU/IMU_Cal_Servo", Float64, queue_size=10)

    rospy.init_node('BNO055_IMU')

    pwm_offset_ms = rospy.get_param("~pwm_offset_ms", 0)  # 0.10

    rate = rospy.Rate(10)

    # wiggle servo
    servo_cal_roll(pub_servo)

    while not rospy.is_shutdown():
        sys_cal, gyro_cal, accel_cal, mag_cal = bno.calibration_status
        yaw, pitch, roll = bno.euler

        if cal is True and yaw != None:
            HEADING_OFFSET = -yaw
            cal = False
        
        yaw += HEADING_OFFSET
        yaw %= 360
        # if necessary
        #m_x, m_y, m_z = bno.read_magnetometer()
        #g_x, g_y, g_z = bno.read_gyroscope()
        #a_x, a_y, a_z = bno.read_accelerometer()
        #                bno.read_linear_acceleration()
        #                bno.read_gravity()

        pub_sys_cal.publish(sys_cal)
        pub_cal.publish(gyro_cal, accel_cal, mag_cal)
        pub_angle.publish(roll, pitch, yaw)

        # if necessary
        #pub_gyro_raw.publish(g_x, g_y, g_z)
        #pub_accel_raw.publish(a_x, a_y, a_z)
        #pub_mag_raw.publish(m_x, m_y, m_z)

        rate.sleep()


if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
