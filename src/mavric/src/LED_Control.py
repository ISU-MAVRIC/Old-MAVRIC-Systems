#!/usr/bin/env python3
import rospy
from abc import ABC, abstractmethod
from mavric.msg import LED
from LED import LightPole 
import Jetson.GPIO as GPIO  
import sys
os.environ["BLINKA_FT232H"] = "1" 1
import board 


light_pole = LightPole()
#CLass brought from Nihaals Led.py script 
class LED(ABC):

    def __init__(self):
        self.toggled = False

    def toggle(self):
        self.toggled = not self.toggled
    
    def isToggled(self):
        return self.toggled

    @abstractmethod
    def setColor(self):
        pass

    @abstractmethod
    def setBrightness(self):
        pass 


def light_pole_callback(data):
    light_pole.setColor(data.color)
    light_pole.setBrightness(data.brightness)
    if (data.toggle != light_pole.isToggled()):
        light_pole.toggle()
    
def listener():
    rospy.init_node('LED_Control', anonymous=True)
    rospy.Subscriber("/indicators/light_pole", LED, light_pole_callback)
    rospy.spin()

if __name__ == '__main__':
    try:
        listener()
    except rospy.ROSInterruptException:
        pass
