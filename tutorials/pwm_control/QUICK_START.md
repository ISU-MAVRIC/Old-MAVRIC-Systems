# Quick Start Guide - PWM Claw Control Tutorial

## 30-Second Overview

Want to control the MAVRIC claw servo without ROS? Start here!

## Prerequisites
```bash
# Enable I2C (if not already done)
sudo raspi-config  # Interface Options -> I2C -> Enable

# Install Python library
pip3 install smbus2

# Test hardware connection
sudo i2cdetect -y 1  # Should see "40" in the output
```

## Run the Demos

### Option 1: Basic PWM (Learn the fundamentals)
```bash
cd tutorials/pwm_control
sudo python3 basic_pwm_example.py
```
**Shows**: PWM duty cycles, frequency control, channel management

### Option 2: Claw Demo (See it in action)
```bash
sudo python3 claw_servo_example.py
```
**Shows**: Open/close/neutral positions, position sweeps, pulse width control

### Option 3: Interactive Control (Hands-on)
```bash
sudo python3 claw_servo_example.py --interactive
```
**Commands**:
- `o` = Open claw
- `c` = Close claw
- `n` = Neutral
- `p -50` = Set position to -50%
- `t 1.5` = Set pulse to 1.5ms
- `q` = Quit

## Understanding the Code

### From ROS to Tutorial

**ROS Way** (requires full ROS stack):
```bash
roslaunch mavric Servos.launch
rostopic pub /Servo/ClawActuation std_msgs/Float64 "data: 50"
```

**Tutorial Way** (standalone Python):
```python
import PCA9685
pwm = PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(50)
pwm.set_pwm(channel=3, on=0, off=2048)  # 50% duty cycle
```

**Tutorial Way** (using helper class):
```python
from claw_servo_example import ClawController
import PCA9685

pwm = PCA9685.PCA9685(address=0x40)
claw = ClawController(pwm, channel=3)
claw.open_claw()
claw.close_claw()
claw.set_position_percent(50)
```

## Key Concepts

### PWM Values
- **4096 steps**: 0 (always off) to 4095 (always on)
- **50% duty**: `pwm.set_pwm(ch, 0, 2048)`
- **25% duty**: `pwm.set_pwm(ch, 0, 1024)`

### Servo Control
- **Frequency**: 50 Hz (standard for servos)
- **1.0 ms pulse**: Fully closed (~5% duty = ~205 PWM value)
- **1.5 ms pulse**: Neutral (~7.5% duty = ~307 PWM value)
- **2.0 ms pulse**: Fully open (~10% duty = ~410 PWM value)

### Channel Assignment
Based on `Servos.launch`:
- **CH3**: Claw actuation (science mode)
- **CH4**: Luminometer (science mode)
- **CH5**: Button pusher (science mode)

## Troubleshooting in 60 Seconds

| Problem | Solution |
|---------|----------|
| Permission denied | Add `sudo` before command |
| No such device | Enable I2C in `raspi-config` |
| Import error | Run `pip3 install smbus2` |
| Servo not moving | Check power supply (5-6V) |
| Wrong movement | Try different channel (3 or 4) |

## File Guide

| Want to... | Read/Run... |
|------------|-------------|
| Learn PWM basics | `basic_pwm_example.py` |
| Control the claw | `claw_servo_example.py` |
| Understand hardware | `README.md` (Hardware section) |
| See ROS connection | `README.md` (Connection section) |
| Debug issues | `README.md` (Troubleshooting) |
| Get overview | `TUTORIAL_SUMMARY.md` |

## Where Things Come From

```
ROS Implementation (src/mavric/src/):
├── PCA9685.py ..................... Base PWM library (used by tutorial)
├── PCA9685_PWM_HAT.py ............. ROS integration (explains concepts)
└── launch/Servos.launch ........... Config values (claw on CH3, 50Hz)

Tutorial (tutorials/pwm_control/):
├── basic_pwm_example.py ........... Learn PWM without servos
├── claw_servo_example.py .......... Apply PWM to control claw
└── README.md ...................... Full documentation
```

## Next Steps

1. ✅ Run the demos above
2. 📖 Read `README.md` for deeper understanding
3. 🔍 Compare tutorial code with `src/mavric/src/PCA9685_PWM_HAT.py`
4. 🚀 Apply knowledge to ROS system
5. 🛠️ Modify for your own servos/hardware

## Safety Reminders

⚠️ **Before you start**:
- Don't power servos from Pi's 5V pin (use external supply)
- Start with neutral position
- Don't force servo mechanically
- Verify pulse widths are safe for your servo

## Quick Reference - Common Values

```python
# Initialize
pwm = PCA9685.PCA9685(address=0x40, busnum=1)
pwm.set_pwm_freq(50)

# Claw positions (from Servos.launch config)
# Position formula: pulse_time = (percent * 0.00001) + 0.0015
CLAW_CLOSED = -65  # ~1.435ms pulse
CLAW_NEUTRAL = 0   # ~1.5ms pulse
CLAW_OPEN = 35     # ~1.535ms pulse
```

## Still Stuck?

1. Check you're in the right directory: `cd tutorials/pwm_control`
2. Verify hardware: `sudo i2cdetect -y 1`
3. Read full docs: `less README.md`
4. Check Python version: `python3 --version` (should be 3.x)

---

**That's it!** You're ready to control PWM without ROS. Happy coding! 🤖
