# PWM Control Tutorial - Summary

## Overview
This document summarizes the PWM control tutorials created for the MAVRIC rover system. These tutorials demonstrate how to control the claw servo using PWM **without ROS**, making it easier to learn the fundamentals and test hardware independently.

## Branch Information
**Branch Name**: `tutorial/pwm-claw-control`

This branch was created from the master branch and contains all tutorial code in the `tutorials/pwm_control/` directory.

## What Was Created

### 1. Directory Structure
```
tutorials/
└── pwm_control/
    ├── README.md                    (239 lines - comprehensive documentation)
    ├── basic_pwm_example.py         (102 lines - basic PWM control)
    └── claw_servo_example.py        (276 lines - claw servo control)
```

### 2. Files Description

#### basic_pwm_example.py
- **Purpose**: Introduction to PWM control fundamentals
- **Features**:
  - PCA9685 initialization
  - Setting PWM frequency (50 Hz for servos)
  - Controlling individual channels
  - Controlling all channels simultaneously
  - Duty cycle sweeping demonstration
  - Clear comments explaining 12-bit resolution (0-4095)

#### claw_servo_example.py
- **Purpose**: Specific implementation for claw servo control
- **Features**:
  - `ClawController` class for managing servo
  - Pulse time control (1.0-2.0 ms typical)
  - Position control using percentages (-100 to 100)
  - Implements same linear mapping as ROS system
  - Predefined methods: `open_claw()`, `close_claw()`, `neutral_position()`
  - Automatic demonstration mode
  - Interactive command-line control mode
  - Based on actual ROS configuration from `Servos.launch`

#### README.md
- **Purpose**: Complete tutorial documentation
- **Contents**:
  - Hardware background (PCA9685, servo control basics)
  - Prerequisites and setup instructions
  - File descriptions and usage examples
  - Connection to ROS implementation
  - Configuration value mapping from launch files
  - Comprehensive troubleshooting guide
  - Safety notes
  - Additional resources and links

## Technical Details

### Hardware Used
- **Controller**: PCA9685 (16-channel, 12-bit PWM, I2C)
- **Default Address**: 0x40 (64 decimal)
- **Frequency**: 50 Hz for servos
- **Channels**: 0-15 (claw typically on CH3 or CH4)

### Key Concepts Demonstrated
1. **PWM Basics**: Duty cycle, frequency, pulse width
2. **Servo Control**: 1.0-2.0ms pulse widths at 50Hz
3. **Linear Mapping**: Converting percentages to pulse times
4. **Hardware Interface**: I2C communication with PCA9685

### Mapping from ROS Implementation

**From**: `src/mavric/src/PCA9685.py` (Adafruit library)
- Base PCA9685 control methods
- I2C communication
- Frequency and duty cycle setting

**From**: `src/mavric/src/PCA9685_PWM_HAT.py` (ROS integration)
- Time-based callback logic
- Pulse width to PWM value conversion
- Multi-channel subscription pattern

**From**: `src/mavric/launch/Servos.launch` (Configuration)
- Claw channel assignment (CH3)
- Linear mapping parameters (slope, intercept)
- Position limits (-65 to 35 for science mode)
- Frequency (50 Hz)
- Clock error correction (1.04166667)

### Tutorial vs ROS Differences

| Aspect | ROS Version | Tutorial Version |
|--------|-------------|------------------|
| Control Method | ROS topics | Direct function calls |
| Configuration | Launch file params | Hardcoded/CLI args |
| Operation Mode | Continuous (rospy.spin) | Sequential/Interactive |
| Dependencies | ROS, rospy, std_msgs | Only PCA9685.py, smbus2 |
| Use Case | Production system | Learning, testing, debugging |

## How to Use

### Setup
1. Clone repository and checkout tutorial branch:
   ```bash
   git clone https://github.com/ISU-MAVRIC/Old-MAVRIC-Systems.git
   cd Old-MAVRIC-Systems
   git checkout tutorial/pwm-claw-control
   ```

2. On Raspberry Pi with I2C enabled:
   ```bash
   sudo apt-get install python3-smbus
   pip3 install smbus2
   ```

3. Connect PCA9685 HAT and servo

### Running Tutorials

**Basic PWM Example**:
```bash
cd tutorials/pwm_control
sudo python3 basic_pwm_example.py
```

**Claw Demo**:
```bash
sudo python3 claw_servo_example.py
```

**Claw Interactive Mode**:
```bash
sudo python3 claw_servo_example.py --interactive
```

## Learning Path

1. **Start with**: `README.md` - Understand hardware and concepts
2. **Run**: `basic_pwm_example.py` - Learn PWM fundamentals
3. **Run**: `claw_servo_example.py` - See servo control in action
4. **Experiment**: Interactive mode - Try different positions
5. **Study**: Compare with ROS implementation in `src/mavric/src/`
6. **Apply**: Use knowledge to work with ROS system

## Testing and Validation

- ✅ Python syntax validated with `py_compile`
- ✅ Code structure follows Python best practices
- ✅ Comprehensive error handling and user feedback
- ✅ Based on proven ROS implementation
- ✅ Includes safety notes and troubleshooting

## Safety Considerations

The tutorials include multiple safety features:
- Clear warnings about power supply requirements
- Servo position limits documented
- Gradual position changes in demos
- Emergency stop capability (Ctrl+C)
- Neutral position return before shutdown

## Future Enhancements

Possible additions (not included in this implementation):
- Multi-servo coordination examples
- Position feedback reading
- Advanced timing examples
- LED control examples
- Integration with sensors
- Web interface for remote control

## Benefits of This Approach

1. **Learning**: Understand PWM fundamentals before ROS complexity
2. **Testing**: Verify hardware without full ROS stack
3. **Debugging**: Isolate problems to hardware vs software
4. **Development**: Rapid prototyping of new servo controls
5. **Documentation**: Clear examples for new team members

## Repository Notes

- Repository is archived (see README.md)
- Current development moved to ROS 2 version
- These tutorials remain valid for understanding PWM fundamentals
- Hardware principles apply to both ROS 1 and ROS 2

## Questions or Issues

For questions about these tutorials:
1. Read the comprehensive README.md in tutorials/pwm_control/
2. Check troubleshooting section
3. Compare with ROS implementation
4. Contact MAVRIC Systems Team Lead

## Commit Information

- **Commit**: Add PWM control tutorials without ROS
- **Files**: 3 files added, 617 lines total
- **Branch**: tutorial/pwm-claw-control
- **Based on**: Master branch (commit 06088c0)

---

Created: September 30, 2024
Author: GitHub Copilot
Repository: ISU-MAVRIC/Old-MAVRIC-Systems
