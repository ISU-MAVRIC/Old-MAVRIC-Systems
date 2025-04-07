#!/usr/bin/env python3
'''
Description:
    Reads voltages from analog to digital converter and 
    converts them to raw battery voltage for the drive
    and system batteries.
Author: 
    Nathan Logston

Topics:
    Publishers:
        Voltage_Monitor
            Batt1
            Batt2
    Subscribers:
        None
'''
import rospy
import board
from std_msgs.msg import Float64
from mavric.msg import Voltage
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15 import analog_in
import Adafruit_ADS1x15 as ADS

def talker():
    volt_pub = rospy.Publisher("ADC", Voltage, queue_size=10)
    voltperCell_pub = rospy.Publisher("ADCpCell", Voltage, queue_size=10)
    rospy.init_node("ADC_Pub")
    rate = rospy.Rate(0.25)
    voltages = Voltage()
    voltpcell = Voltage()
    adc = ADS.ADS1115(busnum=1)
    # Resistors
    B1R1 = 5197
    B1R2 = 995
    B2R1 = 5202
    B2R2 = 997
    B1C = 6
    B2C = 4
    # Ratios are V_Bat/V_divider
    B1Ratio = (B1R1+B1R2)/B1R2
    B2Ratio = (B2R1+B2R2)/B2R2
    VMax1 = 4.09
    VMax2 = 4.1
    ADCMax = 32767
    while not rospy.is_shutdown():
            adc1 = adc.read_adc(0)*VMax1/ADCMax
            adc2 = adc.read_adc(1)*VMax2/ADCMax
            voltages.batt1 = adc1*B1Ratio
            voltages.batt2 = adc2*B2Ratio
            voltpcell.batt1 = voltages.batt1 / B1C
            voltpcell.batt2 = voltages.batt2 / B2C
            volt_pub.publish(voltages)
            voltperCell_pub.publish(voltpcell)
            rate.sleep()



if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
