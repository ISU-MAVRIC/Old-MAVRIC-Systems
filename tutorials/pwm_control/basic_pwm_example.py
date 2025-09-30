#!/usr/bin/env python3
"""
Basic PWM Control Example (Without ROS)

This tutorial demonstrates how to use the PCA9685 PWM controller
without ROS integration. This is useful for testing hardware or
creating standalone applications.

Hardware Requirements:
- PCA9685 PWM HAT or breakout board
- I2C connection to Raspberry Pi or similar
- Power supply for the PCA9685 (if driving servos/motors)

The PCA9685 is a 16-channel, 12-bit PWM controller that communicates
over I2C. It's commonly used for controlling servos and LEDs.
"""

import sys
import time

# Add the mavric src directory to Python path to use the PCA9685 library
# Adjust this path based on where you run the script from
sys.path.insert(0, '../../src/mavric/src')

import PCA9685

def main():
    """
    Basic example showing how to initialize and control PWM outputs
    """
    
    # Initialize the PCA9685 
    # Default I2C address is 0x40 (64 decimal)
    # Default I2C bus is 1
    print("Initializing PCA9685 PWM controller...")
    pwm = PCA9685.PCA9685(address=0x40, busnum=1)
    
    # Set PWM frequency
    # For servos, typically use 50 Hz (50 pulses per second)
    # For LEDs, you might use higher frequencies (100-1000 Hz)
    frequency = 50  # Hz
    print(f"Setting PWM frequency to {frequency} Hz")
    pwm.set_pwm_freq(frequency)
    
    # PWM channels are numbered 0-15
    channel = 0
    
    print("\nExample 1: Setting PWM using raw values")
    print("PWM uses 12-bit resolution (0-4095)")
    print("set_pwm(channel, on_time, off_time)")
    
    # The PCA9685 has 4096 steps in each PWM cycle
    # on_time: when in the cycle to turn on (typically 0)
    # off_time: when in the cycle to turn off (0-4095)
    
    # Example: 50% duty cycle
    pwm.set_pwm(channel, 0, 2048)  # Off at halfway point
    print(f"Channel {channel}: 50% duty cycle (on=0, off=2048)")
    time.sleep(2)
    
    # Example: 25% duty cycle
    pwm.set_pwm(channel, 0, 1024)  # Off at 1/4 point
    print(f"Channel {channel}: 25% duty cycle (on=0, off=1024)")
    time.sleep(2)
    
    # Example: 75% duty cycle  
    pwm.set_pwm(channel, 0, 3072)  # Off at 3/4 point
    print(f"Channel {channel}: 75% duty cycle (on=0, off=3072)")
    time.sleep(2)
    
    print("\nExample 2: Controlling all channels simultaneously")
    # Set all 16 channels to the same value
    pwm.set_all_pwm(0, 2048)  # All channels to 50%
    print("All channels set to 50% duty cycle")
    time.sleep(2)
    
    print("\nExample 3: Sweeping through different PWM values")
    # Sweep from 0% to 100% duty cycle
    for duty in range(0, 4096, 256):
        pwm.set_pwm(channel, 0, duty)
        percent = (duty / 4095.0) * 100
        print(f"Duty cycle: {percent:.1f}%", end='\r')
        time.sleep(0.1)
    print()
    
    # Turn off all channels when done
    print("\nTurning off all channels...")
    pwm.set_all_pwm(0, 0)
    print("Done!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure:")
        print("  1. I2C is enabled on your system")
        print("  2. PCA9685 is connected and powered")
        print("  3. You have proper permissions (may need sudo)")
        print("  4. The smbus2 library is installed: pip3 install smbus2")
