#!/usr/bin/env python3

import rospy, time, os, sys
from std_msgs.msg import String, Bool
os.environ["BLINKA_FT232H"] = "1"
import neopixel_spi as neopixel
import board
state = None
override = False

def state_cb(data):
    global state
    state = data.data

def complete_cb(data):
    global override
    override = data.data

def listener():
    global state, override
    NUM_PIXELS = 31
    PIXEL_ORDER = neopixel.GRB
    spi = board.SPI()
    strip = neopixel.NeoPixel_SPI(spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=True)
    red = 0xFF0000
    green = 0x00FF00
    blue = 0x0000FF
    pulseRed = (0xFF0000, 0xEE0000, 0xDD0000, 0xCC0000, 0xBB0000, 0xAA0000, 0x990000, 0x880000, 0x770000, 0x660000, 0x550000, 0x440000, 0x330000, 0x220000, 0x110000, 0x000000)

    rospy.init_node("LED_Strip")
    state_sub = rospy.Subscriber('State', String, state_cb)
    complete_sub = rospy.Subscriber('Success', Bool, complete_cb)
    rate = rospy.Rate(1)
    while not rospy.is_shutdown():
        if override:
            for i in range(5):
                strip.fill(green)
                time.sleep(0.25)
                strip.fill(0)
                time.sleep(0.25)
            override = False
        else:
            if state == "Idle":
                strip.fill(red)

            elif state == "TurnTowardWaypoint":
                strip.fill(red)
                time.sleep(1)
                strip.fill(0)
                time.sleep(1)

            elif state == "DriveTowardWaypoint":
                for i in pulseRed:
                    strip.fill(i)
                    time.sleep(0.02)
                for i in pulseRed:
                    strip.fill(i)
                    time.sleep(0.02)

            elif state == "Teleop":
                strip.fill(blue)

            elif state == "ReachedWaypoint":
                for i in range(5):
                    strip.fill(red)
                    time.sleep(0.25)
                    strip.fill(0)
                    time.sleep(0.25)

            elif state == "TagFinder":
                for i in range(3):
                    strip.fill(red)
                    time.sleep(0.1)
                    strip.fill(0)
                    time.sleep(0.1)
                time.sleep(0.5)
            elif state == "DriveTowardTag":
                for i in range(3):
                    strip.fill(red)
                    time.sleep(0.2)
                    strip.fill(0)
                    time.sleep(0.2)
                time.sleep(0.5)
            else:
                strip.fill(0)
        rate.sleep()
    strip.fill(0)


if __name__ == '__main__':
    try:
        listener()
    except rospy.ROSInterruptException:
        pass