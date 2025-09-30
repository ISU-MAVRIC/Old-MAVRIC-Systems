# ROS vs Tutorial Code Comparison

This document shows side-by-side comparisons of how the same PWM control operations are performed in the ROS system versus the standalone tutorial code.

## Architecture Comparison

### ROS Architecture (Production System)
```
Base Station (phoenix.py)
    ↓ sends socket commands
Rover Server
    ↓ publishes ROS topic
/Servo/ClawActuation
    ↓ processed by
LinearMapping.py
    ↓ publishes to
/SlowPWM/CH3
    ↓ subscribed by
PCA9685_PWM_HAT.py
    ↓ calls
PCA9685.py library
    ↓ controls
PCA9685 Hardware
    ↓ drives
Servo Motor (Claw)
```

### Tutorial Architecture (Standalone)
```
Python Script (claw_servo_example.py)
    ↓ imports
PCA9685.py library
    ↓ controls
PCA9685 Hardware
    ↓ drives
Servo Motor (Claw)
```

## Code Comparison

### Example 1: Initialization

**ROS Version** (PCA9685_PWM_HAT.py):
```python
import rospy
from std_msgs.msg import Float64
import PCA9685

def listener():
    rospy.init_node('PCA9685_PWM_HAT')
    freq = rospy.get_param('~frequency', 50)
    address = rospy.get_param('~address', 0x40)
    
    pwm = PCA9685.PCA9685(address=address)
    pwm.set_pwm_freq(freq)
    
    # Subscribe to topics...
    rospy.spin()
```

**Tutorial Version** (claw_servo_example.py):
```python
import PCA9685

# Direct initialization - no ROS needed
pwm = PCA9685.PCA9685(address=0x40, busnum=1)
pwm.set_pwm_freq(50)
```

### Example 2: Setting Pulse Time

**ROS Version** (PCA9685_PWM_HAT.py):
```python
def time_callback(data, channel):
    if pwm == None:
        return
    time = data.data  # Time in seconds from ROS message
    percent = time/period
    pwm.set_pwm(channel, 0, int(percent*4095+0.5))
```

**Tutorial Version** (claw_servo_example.py):
```python
def set_pulse_time(self, pulse_ms):
    """Set servo position using pulse time in milliseconds"""
    pulse_seconds = pulse_ms / 1000.0
    percent = pulse_seconds / self.period
    pwm_value = int(percent * 4095 + 0.5)
    pwm_value = max(0, min(4095, pwm_value))
    self.pwm.set_pwm(self.channel, 0, pwm_value)
```

**Key Difference**: Tutorial adds bounds checking and uses milliseconds for user convenience.

### Example 3: Position Control with Linear Mapping

**ROS Version** (Servos.launch + LinearMapping.py):
```xml
<!-- In Servos.launch -->
<node name="ClawActuation_Scale" pkg="mavric" type="LinearMapping.py">
    <param name="inputs"  value="ClawActuation" />
    <param name="outputs" value="/SlowPWM/CH3" />
    <param name="slopes"      value="0.00001" />
    <param name="intercepts"  value="0.0015" />
    <param name="lowLimit" value="-65" />
    <param name="highLimit" value="35" />
</node>
```

```python
# LinearMapping.py applies: output = (input * slope) + intercept
# Then publishes to /SlowPWM/CH3
```

**Tutorial Version** (claw_servo_example.py):
```python
def set_position_percent(self, percent):
    """
    Set servo position as a percentage (-100 to 100)
    Same math as ROS LinearMapping.py
    """
    slope = 0.001 / 100.0  # 0.00001
    intercept = 0.0015     # 1.5ms neutral
    
    pulse_seconds = (percent * slope) + intercept
    pulse_ms = pulse_seconds * 1000.0
    self.set_pulse_time(pulse_ms)
```

**Key Difference**: Tutorial combines the linear mapping and PWM control in one place.

### Example 4: Control Commands

**ROS Version** (Base Station to Rover):
```bash
# Launch the system
roslaunch mavric Servos.launch

# Command from another terminal
rostopic pub /Servo/ClawActuation std_msgs/Float64 "data: -65"  # Close
rostopic pub /Servo/ClawActuation std_msgs/Float64 "data: 0"    # Neutral
rostopic pub /Servo/ClawActuation std_msgs/Float64 "data: 35"   # Open
```

**Tutorial Version**:
```python
# In Python script or interactive mode
claw = ClawController(pwm, channel=3)

claw.close_claw()           # Sets position to -65
claw.neutral_position()     # Sets position to 0
claw.open_claw()            # Sets position to 35

# Or direct control
claw.set_position_percent(-65)
claw.set_position_percent(0)
claw.set_position_percent(35)
```

**Interactive Mode**:
```bash
sudo python3 claw_servo_example.py --interactive
> c  # Close
> n  # Neutral
> o  # Open
```

## Configuration Comparison

### ROS Configuration (Launch Files)

**From Servos.launch**:
```xml
<node name="SlowPWM_HAT" pkg="mavric" type="PCA9685_PWM_HAT.py">
    <param name="container" value="SlowPWM/" />
    <param name="control_mode" value="PulseTime" />
    <param name="frequency" value="50" />
    <param name="address" value="64" />  <!-- 0x40 in hex -->
    <param name="clk_error" value="1.04166667" />
</node>
```

### Tutorial Configuration (Hardcoded)

```python
class ClawController:
    def __init__(self, pwm, channel, frequency=50):
        self.frequency = frequency
        # Equivalent to ROS params but hardcoded
        
# In main():
pwm = PCA9685.PCA9685(address=0x40, busnum=1)  # address=64 decimal
claw = ClawController(pwm, channel=3, frequency=50)
```

## Feature Comparison Table

| Feature | ROS Version | Tutorial Version |
|---------|-------------|------------------|
| **Setup Complexity** | High (ROS installation, launch files, nodes) | Low (Python + smbus2) |
| **Configuration** | Launch file parameters | Hardcoded or CLI args |
| **Control Method** | ROS topics | Direct function calls |
| **Real-time Updates** | Yes (continuous) | Manual/sequential |
| **Network Control** | Yes (ROS master) | No (local only) |
| **Learning Curve** | Steep | Gentle |
| **Production Ready** | Yes | No (educational) |
| **Debugging** | Complex | Simple |
| **Hardware Access** | Through ROS nodes | Direct |
| **Documentation** | Distributed | Self-contained |

## When to Use Each Approach

### Use ROS Version When:
- ✅ Running the full rover system
- ✅ Need coordination between multiple subsystems
- ✅ Remote control required
- ✅ Real-time operation needed
- ✅ Integration with other ROS nodes
- ✅ Production environment

### Use Tutorial Version When:
- ✅ Learning PWM basics
- ✅ Testing hardware without ROS
- ✅ Debugging servo issues
- ✅ Rapid prototyping
- ✅ Demonstrating concepts
- ✅ No ROS available
- ✅ Educational purposes

## Migration Path: Tutorial → ROS

If you've learned with the tutorial and want to use ROS:

1. **Understand the hardware** (tutorial provides this)
2. **Learn ROS basics** (topics, nodes, launch files)
3. **Study PCA9685_PWM_HAT.py** to see ROS integration
4. **Review launch files** to understand configuration
5. **Use rostopic** to control from command line
6. **Integrate** with other rover systems

## Code Reusability

The `PCA9685.py` library is shared between both:
- ✅ ROS version imports it: `import PCA9685`
- ✅ Tutorial imports it: `import PCA9685`
- ✅ Same API, same hardware control
- ✅ Only the wrapper/interface differs

## Summary

The tutorial version **simplifies** the ROS implementation by:
1. Removing ROS dependencies
2. Combining multiple layers into one
3. Making configuration explicit
4. Providing interactive control
5. Adding educational comments

The ROS version **extends** the basic concept by:
1. Adding network communication
2. Enabling distributed control
3. Providing real-time updates
4. Integrating with other systems
5. Making it production-ready

Both use the **same fundamental PWM control** through PCA9685.py!

---

**Next Steps**: 
1. Master the tutorial version
2. Compare with ROS code in `src/mavric/src/`
3. Understand the extra layers ROS adds
4. Apply knowledge to the full rover system
