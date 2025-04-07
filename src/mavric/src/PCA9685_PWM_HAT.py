#!/usr/bin/env python3

# Subscribes to a topic for each PWM output, setting the output accordingly.
# Each topic is a std_msgs/Float64 topic named CH# where # is the channel number (0-15)

# Parameters:
#  ~frequency - the frequency in Hz of the desired PWM, not all frequencies are possible, the library should be using the closest possible frequency (accounting for the clock error)
#  ~clk_error - A calibration parameter for the PWM's clock rate error
#                 A number greater than 1 means that the clock runs faster than it should
#  ~address the I2C address of the PCA9685

# Topics:
#   PWM_Channels/PulseTimeControl/CH# - Subscription: Publish to this topic to set the pulse width of the output. Only as accurate as the period
#   PWM_Channels/DutyCycleControl/CH# - Subscription: Publish to this topic to set the duty cycle of the output. Operates in 4096 steps.

import rospy
from std_msgs.msg import Float64
import PCA9685

pwm = None
period = 0

def time_callback(data, channel):
        if pwm == None:
                return
        time = data.data
        percent = time/period;
        pwm.set_pwm(channel, 0, int(percent*4095+0.5))

def percent_callback(data, channel):
        if pwm == None:
                return
        percent = data.data
        pwm.set_pwm(channel, 0, int(percent*4095+0.5))

def listener():
        global period, pwm
        rospy.init_node('PCA9685_PWM_HAT')
        freq = rospy.get_param('~frequency', 50);
        period = 1./freq
        clk_error = rospy.get_param('~clk_error', 1);
        address = rospy.get_param('~address', 0x40);
        mode = rospy.get_param('~control_mode', "both");
        container = rospy.get_param('~container', "PWM_Channels/");
        
        pwm = PCA9685.PCA9685(address=address)
        print("freq period corrected_freq")
        print(freq, period, freq/clk_error)
        pwm.set_pwm_freq(freq/clk_error)
        for i in range(16):
                if (mode == "DutyCycle"):
                        rospy.Subscriber(container + "CH"+str(i), Float64, percent_callback, i, queue_size=10)
                        
                elif (mode == "PulseTime"):
                        rospy.Subscriber(container + "CH"+str(i), Float64, time_callback, i, queue_size=10)
                
                else: #if (mode == "both"):
                        rospy.Subscriber(container + "PulseTimeControl/CH"+str(i), Float64, time_callback, i, queue_size=10)
                        rospy.Subscriber(container + "DutyCycleControl/CH"+str(i), Float64, percent_callback, i, queue_size=10)

        rospy.spin()



if __name__ == '__main__':
    listener()
