#!/usr/bin/env python3
"""
Claw Servo Control Example (Without ROS)

This tutorial demonstrates how to control a servo motor (like the claw
actuator) using PWM, without ROS integration. This example is based on
the actual claw control implementation used in the MAVRIC rover system.

Hardware Requirements:
- PCA9685 PWM HAT or breakout board
- Servo motor (the claw actuator)
- I2C connection to Raspberry Pi or similar
- External power supply for servos (5-6V typically)

Servo Control Basics:
- Servos typically use 50 Hz PWM signals
- Pulse width determines position:
  * ~1.0 ms pulse = fully closed/one extreme (~5% duty cycle)
  * ~1.5 ms pulse = neutral/center (~7.5% duty cycle)
  * ~2.0 ms pulse = fully open/other extreme (~10% duty cycle)
- Total period at 50Hz = 20ms

Note: The exact pulse widths may vary by servo model. Always test
carefully and avoid forcing the servo beyond its limits.
"""

import sys
import time

# Add the mavric src directory to Python path
sys.path.insert(0, '../../src/mavric/src')

import PCA9685

class ClawController:
    """
    Simple controller for a claw servo using PWM
    
    This class mimics the behavior of the ROS-based claw control
    but operates standalone without ROS dependencies.
    """
    
    def __init__(self, pwm, channel, frequency=50):
        """
        Initialize the claw controller
        
        Args:
            pwm: PCA9685 PWM controller instance
            channel: PWM channel number (0-15) connected to the claw servo
            frequency: PWM frequency in Hz (default 50 for servos)
        """
        self.pwm = pwm
        self.channel = channel
        self.frequency = frequency
        self.period = 1.0 / frequency  # Period in seconds
        
        # Configure PWM frequency
        self.pwm.set_pwm_freq(frequency)
        
        print(f"Claw controller initialized:")
        print(f"  Channel: {channel}")
        print(f"  Frequency: {frequency} Hz")
        print(f"  Period: {self.period*1000:.2f} ms")
    
    def set_pulse_time(self, pulse_ms):
        """
        Set servo position using pulse time in milliseconds
        
        This is the same method used in PCA9685_PWM_HAT.py's time_callback
        
        Args:
            pulse_ms: Pulse width in milliseconds (typically 1.0 - 2.0)
        """
        # Convert pulse time to duty cycle percentage
        pulse_seconds = pulse_ms / 1000.0
        percent = pulse_seconds / self.period
        
        # Convert to 12-bit value (0-4095)
        pwm_value = int(percent * 4095 + 0.5)
        
        # Clamp to valid range
        pwm_value = max(0, min(4095, pwm_value))
        
        # Set the PWM
        self.pwm.set_pwm(self.channel, 0, pwm_value)
        
        print(f"Pulse: {pulse_ms:.3f}ms, Duty: {percent*100:.2f}%, PWM: {pwm_value}")
    
    def set_position_percent(self, percent):
        """
        Set servo position as a percentage (-100 to 100)
        
        Based on the Servos.launch configuration:
        - slope: 0.001/100 = 0.00001
        - intercept: 0.0015 (1.5ms neutral position)
        - limits: -65 to 35 (for science mode) or -20 to 20 (for drive mode)
        
        Args:
            percent: Position percentage (-100 to 100)
                    -100 = fully closed, 0 = neutral, 100 = fully open
        """
        # Apply the same linear mapping as in the ROS system
        # pulse_time = (percent * slope) + intercept
        slope = 0.001 / 100.0  # 0.00001
        intercept = 0.0015     # 1.5ms neutral
        
        pulse_seconds = (percent * slope) + intercept
        pulse_ms = pulse_seconds * 1000.0
        
        self.set_pulse_time(pulse_ms)
    
    def close_claw(self):
        """Fully close the claw"""
        print("Closing claw...")
        self.set_position_percent(-65)
    
    def open_claw(self):
        """Fully open the claw"""
        print("Opening claw...")
        self.set_position_percent(35)
    
    def neutral_position(self):
        """Move to neutral/center position"""
        print("Moving to neutral position...")
        self.set_position_percent(0)
    
    def stop(self):
        """Turn off PWM signal"""
        print("Stopping servo...")
        self.pwm.set_pwm(self.channel, 0, 0)


def main():
    """
    Main demonstration program
    """
    print("=" * 60)
    print("Claw Servo Control Tutorial (Without ROS)")
    print("=" * 60)
    
    # Initialize PCA9685
    # Based on Servos.launch: address=64 (0x40), frequency=50Hz
    print("\nInitializing PCA9685...")
    pwm = PCA9685.PCA9685(address=0x40, busnum=1)
    
    # Claw is on CH3 or CH4 depending on configuration
    # Using CH3 as per Servos.launch
    claw_channel = 3
    
    # Create claw controller
    claw = ClawController(pwm, claw_channel, frequency=50)
    
    print("\n" + "=" * 60)
    print("Starting demonstration sequence")
    print("=" * 60)
    
    # Demo 1: Move to neutral position
    print("\n--- Demo 1: Neutral Position ---")
    claw.neutral_position()
    time.sleep(2)
    
    # Demo 2: Close the claw
    print("\n--- Demo 2: Close Claw ---")
    claw.close_claw()
    time.sleep(2)
    
    # Demo 3: Open the claw
    print("\n--- Demo 3: Open Claw ---")
    claw.open_claw()
    time.sleep(2)
    
    # Demo 4: Sweep through positions
    print("\n--- Demo 4: Position Sweep ---")
    print("Sweeping from closed (-65) to open (35)...")
    for pos in range(-65, 36, 5):
        claw.set_position_percent(pos)
        time.sleep(0.2)
    
    # Demo 5: Manual pulse width control
    print("\n--- Demo 5: Manual Pulse Width Control ---")
    print("Testing different pulse widths...")
    
    pulse_widths = [1.0, 1.25, 1.5, 1.75, 2.0]
    for pulse in pulse_widths:
        print(f"\nSetting pulse width to {pulse} ms")
        claw.set_pulse_time(pulse)
        time.sleep(1.5)
    
    # Return to neutral and stop
    print("\n--- Finishing Up ---")
    claw.neutral_position()
    time.sleep(1)
    claw.stop()
    
    print("\n" + "=" * 60)
    print("Tutorial complete!")
    print("=" * 60)


def interactive_mode():
    """
    Interactive mode for manual control
    """
    print("=" * 60)
    print("Interactive Claw Control Mode")
    print("=" * 60)
    
    pwm = PCA9685.PCA9685(address=0x40, busnum=1)
    claw_channel = 3
    claw = ClawController(pwm, claw_channel, frequency=50)
    
    print("\nCommands:")
    print("  'o' - Open claw")
    print("  'c' - Close claw")
    print("  'n' - Neutral position")
    print("  'p <percent>' - Set position (-65 to 35)")
    print("  't <ms>' - Set pulse time in milliseconds")
    print("  'q' - Quit")
    
    try:
        while True:
            cmd = input("\nEnter command: ").strip().lower()
            
            if cmd == 'o':
                claw.open_claw()
            elif cmd == 'c':
                claw.close_claw()
            elif cmd == 'n':
                claw.neutral_position()
            elif cmd.startswith('p '):
                try:
                    percent = float(cmd.split()[1])
                    claw.set_position_percent(percent)
                except (ValueError, IndexError):
                    print("Invalid format. Use: p <number>")
            elif cmd.startswith('t '):
                try:
                    pulse_ms = float(cmd.split()[1])
                    claw.set_pulse_time(pulse_ms)
                except (ValueError, IndexError):
                    print("Invalid format. Use: t <number>")
            elif cmd == 'q':
                break
            else:
                print("Unknown command. Type 'o', 'c', 'n', 'p <n>', 't <n>', or 'q'")
    
    finally:
        claw.neutral_position()
        time.sleep(0.5)
        claw.stop()
        print("Exiting...")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Claw servo control tutorial')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Run in interactive mode')
    args = parser.parse_args()
    
    try:
        if args.interactive:
            interactive_mode()
        else:
            main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure I2C is enabled: sudo raspi-config")
        print("  2. Check PCA9685 is connected and powered")
        print("  3. Verify I2C address: sudo i2cdetect -y 1")
        print("  4. Install dependencies: pip3 install smbus2")
        print("  5. May need sudo permissions: sudo python3 claw_servo_example.py")
