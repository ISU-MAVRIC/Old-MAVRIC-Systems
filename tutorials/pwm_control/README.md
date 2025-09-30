# PWM Control Tutorials (Without ROS)

This directory contains tutorial code demonstrating how to control PWM outputs using the PCA9685 controller **without ROS**. These tutorials are based on the actual implementation used in the MAVRIC rover system but simplified for standalone use.

## Overview

The MAVRIC rover uses a PCA9685 PWM HAT to control servos, including the claw actuator. The ROS workspace contains code that integrates this hardware with ROS topics, but sometimes you need to:
- Test hardware without running the full ROS system
- Learn how PWM control works at a fundamental level
- Create standalone applications or diagnostic tools
- Understand the underlying hardware before working with ROS

These tutorials provide that foundation.

## Hardware Background

### PCA9685 PWM Controller
- **Type**: 16-channel, 12-bit PWM controller
- **Interface**: I2C (default address: 0x40)
- **Resolution**: 4096 steps per PWM cycle (12-bit)
- **Frequency Range**: 24 Hz to 1526 Hz
- **Common Uses**: Servo motors, LED control
- **Library Source**: Based on Adafruit's PCA9685 Python library

### Servo Control Basics
Servos typically use PWM signals at 50 Hz:
- **Period**: 20 ms (1/50 Hz)
- **Pulse Width**: 1.0 - 2.0 ms typically
  - 1.0 ms ≈ 0° or fully closed (5% duty cycle)
  - 1.5 ms ≈ 90° or neutral (7.5% duty cycle)
  - 2.0 ms ≈ 180° or fully open (10% duty cycle)

The exact range depends on your specific servo model.

## Files in This Directory

### 1. `basic_pwm_example.py`
**Purpose**: Introduction to PWM control

**What it demonstrates**:
- Initializing the PCA9685 controller
- Setting PWM frequency
- Controlling individual channels with raw values
- Controlling all channels simultaneously
- Sweeping through different duty cycles

**Run it**:
```bash
cd tutorials/pwm_control
sudo python3 basic_pwm_example.py
```

### 2. `claw_servo_example.py`
**Purpose**: Specific example for controlling the claw servo

**What it demonstrates**:
- Servo-specific PWM timing (pulse width control)
- Position control using percentage (-100 to 100)
- Implementing the same linear mapping used in ROS
- Claw open/close/neutral positions
- Both automatic demo mode and interactive control

**Run it**:
```bash
# Automatic demonstration
cd tutorials/pwm_control
sudo python3 claw_servo_example.py

# Interactive mode (manual control)
sudo python3 claw_servo_example.py --interactive
```

**Interactive commands**:
- `o` - Open claw
- `c` - Close claw  
- `n` - Neutral position
- `p <number>` - Set position as percentage (e.g., `p -50`)
- `t <number>` - Set pulse time in milliseconds (e.g., `t 1.5`)
- `q` - Quit

## Prerequisites

### Hardware
1. PCA9685 PWM HAT or breakout board
2. I2C connection to Raspberry Pi or compatible system
3. Servo motor (for claw example)
4. External power supply (5-6V for servos)
   - **Important**: Servos draw significant current; don't power from Pi's 5V rail

### Software
1. **Enable I2C** on your Raspberry Pi:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options -> I2C -> Enable
   ```

2. **Install Python dependencies**:
   ```bash
   pip3 install smbus2
   ```

3. **Test I2C connection**:
   ```bash
   sudo i2cdetect -y 1
   ```
   You should see `40` (0x40) in the output if PCA9685 is connected.

### Permissions
PWM control requires I2C access, which typically needs root permissions:
```bash
sudo python3 basic_pwm_example.py
```

Or add your user to the i2c group:
```bash
sudo usermod -a -G i2c $USER
# Then log out and back in
```

## Connection to ROS Implementation

These tutorials are based on the actual ROS code found in:
- `src/mavric/src/PCA9685.py` - Base PCA9685 library
- `src/mavric/src/PCA9685_PWM_HAT.py` - ROS integration layer
- `src/mavric/launch/Servos.launch` - Configuration for claw and other servos
- `src/mavric/launch/Arm.launch` - Arm system launch configuration

### Key Differences

**ROS Version** (`PCA9685_PWM_HAT.py`):
- Subscribes to ROS topics for control
- Uses ROS parameters for configuration
- Integrates with broader ROS system
- Runs continuously with `rospy.spin()`

**Tutorial Version** (these files):
- Direct Python function calls
- Hardcoded or command-line configuration
- Standalone operation
- Runs defined sequences or interactive mode

### Mapping to ROS Topics

In the ROS system, the claw is controlled via:
```
Topic: /Servo/ClawActuation
  ↓ (LinearMapping.py applies scaling)
Topic: /SlowPWM/CH3
  ↓ (PCA9685_PWM_HAT.py converts to PWM)
Hardware: PCA9685 channel 3
```

In the tutorial, this is simplified to:
```python
claw.set_position_percent(-50)  # Direct control
```

### Configuration Values from Launch Files

From `Servos.launch`:
```xml
<param name="slopes" value="0.00001" />      <!-- 0.001/100 -->
<param name="intercepts" value="0.0015" />   <!-- 1.5ms neutral -->
<param name="lowLimit" value="-65" />        <!-- Science mode -->
<param name="highLimit" value="35" />
```

These are replicated in `claw_servo_example.py`:
```python
slope = 0.001 / 100.0
intercept = 0.0015
```

## Troubleshooting

### "Permission denied" on I2C
**Solution**: Run with sudo or add user to i2c group

### "No such file or directory: '/dev/i2c-1'"
**Solution**: Enable I2C in raspi-config

### PCA9685 not detected
**Solutions**:
1. Check physical connections
2. Verify power supply
3. Run `sudo i2cdetect -y 1` to scan for devices
4. Try different I2C address if board is configured differently

### Servo not responding
**Solutions**:
1. Check servo power supply (separate from Pi)
2. Verify servo is connected to correct channel
3. Try different pulse widths (some servos have different ranges)
4. Check for loose connections

### Servo jittering or unstable
**Solutions**:
1. Ensure adequate power supply current rating
2. Add capacitor near power input (100-1000µF)
3. Verify good ground connection between Pi and PCA9685
4. Reduce PWM frequency if necessary

## Safety Notes

1. **Always** test with low power first
2. **Never** force a servo mechanically - it can damage the gears
3. **Verify** pulse widths are within safe range for your servo
4. **Use** external power for servos, not the Pi's 5V rail
5. **Start** with neutral position before testing extremes
6. **Monitor** servo temperature - overheating indicates problems

## Next Steps

After completing these tutorials:

1. **Understand the code**: Read through both examples to see how they work
2. **Experiment**: Modify the pulse widths and positions to match your hardware
3. **Integrate with ROS**: Study how `PCA9685_PWM_HAT.py` wraps this functionality
4. **Build on it**: Use this knowledge to control other servos or PWM devices
5. **Explore the full system**: Look at the complete ROS launch files and integration

## Additional Resources

- [PCA9685 Datasheet](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf)
- [Adafruit PCA9685 Tutorial](https://learn.adafruit.com/16-channel-pwm-servo-driver)
- [Servo Control Basics](https://learn.sparkfun.com/tutorials/hobby-servo-tutorial)
- [Raspberry Pi I2C Configuration](https://www.raspberrypi.org/documentation/hardware/raspberrypi/i2c/)

## Questions or Issues?

If you encounter issues with these tutorials:
1. Check the troubleshooting section above
2. Verify your hardware setup matches the requirements
3. Compare with the ROS implementation in the src directory
4. Contact the MAVRIC Systems Team Lead

---

**Note**: This repository is archived and not receiving updates due to the ROS 2 migration. For current code, see the [new MAVRIC_Systems repository](https://github.com/ISU-MAVRIC/MAVRIC_Systems).
