# SparkCAN Library Complete Tutorial

This tutorial provides comprehensive documentation for all classes and methods in the SparkCAN library for controlling SparkMax Electronic Speed Controllers via CAN bus.

## Table of Contents
1. [Overview](#overview)
2. [SparkBus Class](#sparkbus-class)
3. [Controller Class](#controller-class)
4. [Status Class](#status-class)
5. [Complete Usage Examples](#complete-usage-examples)
6. [Best Practices](#best-practices)

---

## Overview

The SparkCAN library provides a Python interface for controlling SparkMax Electronic Speed Controllers using a CAN bus. It consists of three main classes:
- **SparkBus**: Manages the CAN bus connection and multiple controllers
- **Controller**: Represents an individual motor controller
- **Status**: Handles decoding of status messages from controllers

---

## SparkBus Class

The SparkBus class is the main entry point for the library. It manages the CAN bus connection and handles communication with multiple motor controllers.

### Constructor

```python
SparkBus(channel='can0', bustype='socketcan', bitrate=1000000)
```

**Description**: Creates a new SparkBus object and initializes the CAN bus connection.

**Parameters**:
- `channel` (str, optional): Serial channel the CAN interface is on. Default: `'can0'`
- `bustype` (str, optional): Type of bus. Set to `None` to let it be resolved automatically. Default: `'socketcan'`
- `bitrate` (int, optional): Rate at which bits are sent through the CAN bus. Default: `1000000`

**Example**:
```python
from SparkCAN import SparkBus

# Create SparkBus with default settings
bus = SparkBus()

# Create SparkBus with custom settings
bus = SparkBus(channel="can1", bustype='socketcan', bitrate=500000)
```

**Notes**:
- The constructor automatically starts two background threads:
  - Heartbeat thread: Sends periodic heartbeat messages to keep controllers enabled
  - Monitor thread: Continuously listens for status messages from controllers

---

### init_controller()

```python
init_controller(canID)
```

**Description**: Initializes a SparkMax controller for sending and receiving messages.

**Parameters**:
- `canID` (int): CAN ID of the controller (1-63)

**Returns**: Controller object

**Example**:
```python
# Initialize controller with CAN ID 1
motor1 = bus.init_controller(1)

# Initialize multiple controllers
motor2 = bus.init_controller(2)
motor3 = bus.init_controller(3)
```

**Notes**:
- Each controller must have a unique CAN ID
- The controller is automatically added to the heartbeat message
- You can initialize up to 64 controllers (IDs 0-63)

---

### send_msg()

```python
send_msg(msg)
```

**Description**: Sends a CAN message to controllers via the CAN bus.

**Parameters**:
- `msg` (Message): CAN message object to be sent

**Example**:
```python
from can import Message

# Create a custom CAN message
msg = Message(arbitration_id=0x02050080, data=[0x00, 0x00, 0x00, 0x00])
bus.send_msg(msg)
```

**Notes**:
- This is a low-level method typically used internally by Controller objects
- Most users should use Controller methods instead of sending raw messages
- Errors are caught and printed but do not raise exceptions

---

### enable_heartbeat()

```python
enable_heartbeat()
```

**Description**: Enables the heartbeat runnable for sending periodic heartbeat messages to the CAN bus.

**Parameters**: None

**Returns**: None

**Example**:
```python
# Enable heartbeat (it's enabled by default)
bus.enable_heartbeat()
```

**Notes**:
- Heartbeat is enabled by default when SparkBus is created
- Heartbeat messages are sent every 20ms (0.02 seconds)
- Heartbeat is required to keep motor controllers active

---

### disable_heartbeat()

```python
disable_heartbeat()
```

**Description**: Disables the heartbeat runnable, stopping periodic heartbeat messages to the CAN bus.

**Parameters**: None

**Returns**: None

**Example**:
```python
# Disable heartbeat (motors will stop responding)
bus.disable_heartbeat()
```

**Notes**:
- Disabling heartbeat will cause motor controllers to stop responding
- Use this for testing or emergency stop situations
- The heartbeat thread continues running but doesn't send messages

---

### bus_monitor() [Internal]

```python
bus_monitor()
```

**Description**: Internal thread method that continuously monitors the CAN bus for incoming status messages from controllers.

**Notes**:
- This method runs in a background daemon thread
- Automatically started when SparkBus is created
- Decodes and routes messages to appropriate Controller objects
- Should not be called directly by users

---

### _update_heartbeat_array() [Internal]

```python
_update_heartbeat_array()
```

**Description**: Internal helper method that updates the heartbeat CAN message array when a new controller is added.

**Notes**:
- Automatically called by `init_controller()`
- Maintains a bitmask of enabled controller IDs
- Should not be called directly by users

---

### _heartbeat_runnable() [Internal]

```python
_heartbeat_runnable()
```

**Description**: Internal thread method that continuously sends heartbeat messages while heartbeat is enabled.

**Notes**:
- Runs in a background daemon thread
- Sends messages every 20ms
- Should not be called directly by users

---

## Controller Class

The Controller class represents an individual SparkMax motor controller and provides methods for controlling the motor and reading feedback.

### Constructor

```python
Controller(bus, id)
```

**Description**: Creates a new Controller object.

**Parameters**:
- `bus` (SparkBus): The SparkBus object managing the CAN connection
- `id` (int): CAN ID of this controller

**Notes**:
- Controllers should be created using `SparkBus.init_controller()` instead of directly
- Controller objects maintain internal properties for direction and scaling

---

### percent_output()

```python
percent_output(value)
```

**Description**: Sets the motor controller to percent output mode with the specified power level.

**Parameters**:
- `value` (float): Output percentage, range -1.0 to 1.0 (where 1.0 = 100% forward, -1.0 = 100% reverse)

**Returns**: None

**Example**:
```python
# Set motor to 50% forward
motor.percent_output(0.5)

# Set motor to 75% reverse
motor.percent_output(-0.75)

# Stop motor
motor.percent_output(0)
```

**Notes**:
- Values are modified by internal `percentProps` (direction and scale)
- Most common control method for simple applications
- **IMPORTANT**: If running at more than 50% power, ramping must be enabled on the controller to prevent stuttering

---

### velocity_output()

```python
velocity_output(value)
```

**Description**: Sets the motor controller to velocity control mode with the specified velocity setpoint.

**Parameters**:
- `value` (float): Target velocity in units per second (units depend on controller configuration)

**Returns**: None

**Example**:
```python
# Set motor to target velocity of 100 units/sec
motor.velocity_output(100)

# Set motor to target velocity of -50 units/sec (reverse)
motor.velocity_output(-50)

# Stop motor
motor.velocity_output(0)
```

**Notes**:
- Values are modified by internal `velocityProps` (direction and count conversion)
- Requires velocity PID to be configured on the SparkMax controller
- Used in `SparkCAN_Drive_Train.py` for wheel speed control
- Velocity units depend on encoder configuration

---

### position_output()

```python
position_output(value)
```

**Description**: Sets the motor controller to position control mode with the specified position setpoint.

**Parameters**:
- `value` (float): Target position in encoder counts or configured units

**Returns**: None

**Example**:
```python
# Set motor to target position of 1000 counts
motor.position_output(1000)

# Set motor to target position of -500 counts
motor.position_output(-500)

# Return to zero position
motor.position_output(0)
```

**Notes**:
- Values are modified by internal `positionProps` (direction and count conversion)
- Requires position PID to be configured on the SparkMax controller
- Used in `SparkCAN_Drive_Train.py` for steering position control
- Position units depend on encoder configuration

---

### velocity [Property]

```python
motor.velocity
```

**Description**: Read-only property that returns the current velocity from the motor controller.

**Returns**: float - Current velocity in units per second

**Example**:
```python
# Read current velocity
current_speed = motor.velocity
print(f"Motor velocity: {current_speed}")

# Monitor velocity while motor is running
motor.velocity_output(100)
for i in range(10):
    print(f"Current velocity: {motor.velocity}")
    time.sleep(0.1)
```

**Notes**:
- Data comes from Status message 0x61
- Updated continuously by the bus_monitor thread
- Returns the most recent value received from the controller
- Velocity feedback is available in all control modes

---

### position [Property]

```python
motor.position
```

**Description**: Read-only property that returns the current position from the motor controller.

**Returns**: float - Current position in encoder counts or configured units

**Example**:
```python
# Read current position
current_pos = motor.position
print(f"Motor position: {current_pos}")

# Monitor position while motor is moving
motor.position_output(1000)
while abs(motor.position - 1000) > 10:
    print(f"Current position: {motor.position}")
    time.sleep(0.1)
```

**Notes**:
- Data comes from Status message 0x62
- Updated continuously by the bus_monitor thread
- Returns the most recent value received from the controller
- Position feedback is available in all control modes
- Used in `SparkCAN_Drive_Train.py` for steering feedback

---

### enable() [Not Implemented]

```python
enable()
```

**Description**: Intended to send an enable control message to the motor controller.

**Status**: **NOT IMPLEMENTED** - Currently a placeholder that does nothing

**Notes**:
- Method exists but contains only `pass`
- Motor controllers are enabled via heartbeat messages instead
- Future implementation may provide explicit enable control

---

### disable() [Not Implemented]

```python
disable()
```

**Description**: Intended to send a disable control message to the motor controller.

**Status**: **NOT IMPLEMENTED** - Currently a placeholder that does nothing

**Notes**:
- Method exists but contains only `pass`
- To disable motors, use `disable_heartbeat()` on the SparkBus object
- Future implementation may provide explicit disable control

---

## Status Class

The Status class handles decoding of status messages received from motor controllers.

### Constructor

```python
Status(id, datasizes, datatypes)
```

**Description**: Creates a new Status object for decoding CAN status messages.

**Parameters**:
- `id` (int): Full CAN arbitration ID of the status message
- `datasizes` (tuple): Sizes in bits of each data partition in the message
- `datatypes` (tuple): Data types of each partition ('float', 'int', or 'uint')

**Example**:
```python
# Create a Status decoder for velocity status (0x61)
velocity_status = Status(0x2051840 + controller_id, (32, 8, 12, 12), ('float', 'uint', 'uint', 'uint'))

# Create a Status decoder for position status (0x62)
position_status = Status(0x2051880 + controller_id, (32,), ('float',))
```

**Notes**:
- Typically created internally by Controller objects
- Most users don't need to create Status objects directly

---

### decode()

```python
decode(msg)
```

**Description**: Decodes a CAN message into its individual data values.

**Parameters**:
- `msg` (bytes): Raw CAN message data to decode

**Returns**: None (decoded values are stored in `self.data`)

**Example**:
```python
# Decode a message (typically done automatically by bus_monitor)
status.decode(message.data)

# Access decoded values
velocity_value = status.data[0]
```

**Notes**:
- Called automatically by the bus_monitor thread
- Supports float, signed int, and unsigned int data types
- Uses little-endian byte order for floats
- Decoded values are stored in the `data` attribute

---

### get_value()

```python
get_value(index)
```

**Description**: Returns a specific decoded value from the most recent status message.

**Parameters**:
- `index` (int): Index of the desired data value (0-based)

**Returns**: Decoded value (float, int, or uint depending on configuration)

**Example**:
```python
# Get the first decoded value
value = status.get_value(0)

# Get the second decoded value
value2 = status.get_value(1)
```

**Notes**:
- Alternative to accessing `status.data[index]` directly
- Returns the most recently decoded value
- Index must be within range of configured datatypes

---

## Complete Usage Examples

### Example 1: Basic Motor Control

```python
from SparkCAN import SparkBus
import time

# Initialize CAN bus
bus = SparkBus(channel="can0", bustype='socketcan', bitrate=1000000)

# Initialize a motor controller
motor = bus.init_controller(1)

# Wait for initialization
time.sleep(1)

# Ramp motor to 30% power
motor.percent_output(0.3)
time.sleep(2)

# Stop motor
motor.percent_output(0)
```

### Example 2: Velocity Control with Feedback

```python
from SparkCAN import SparkBus
import time

bus = SparkBus(channel="can0", bustype='socketcan', bitrate=1000000)
motor = bus.init_controller(1)
time.sleep(1)

# Set target velocity
target_velocity = 100
motor.velocity_output(target_velocity)

# Monitor velocity for 5 seconds
start_time = time.time()
while time.time() - start_time < 5:
    current_velocity = motor.velocity
    print(f"Target: {target_velocity}, Current: {current_velocity:.2f}")
    time.sleep(0.1)

# Stop motor
motor.velocity_output(0)
```

### Example 3: Position Control

```python
from SparkCAN import SparkBus
import time

bus = SparkBus(channel="can0", bustype='socketcan', bitrate=1000000)
motor = bus.init_controller(1)
time.sleep(1)

# Move to target position
target_position = 1000
motor.position_output(target_position)

# Wait until position is reached (within 10 counts)
while abs(motor.position - target_position) > 10:
    print(f"Current position: {motor.position:.2f}")
    time.sleep(0.1)

print(f"Target position reached: {motor.position:.2f}")
```

### Example 4: Multiple Controllers

```python
from SparkCAN import SparkBus
import time

bus = SparkBus(channel="can0", bustype='socketcan', bitrate=1000000)

# Initialize multiple controllers
left_motor = bus.init_controller(1)
right_motor = bus.init_controller(2)
time.sleep(1)

# Drive both motors forward
left_motor.percent_output(0.5)
right_motor.percent_output(0.5)
time.sleep(2)

# Turn right (left faster, right slower)
left_motor.percent_output(0.7)
right_motor.percent_output(0.3)
time.sleep(1)

# Stop both motors
left_motor.percent_output(0)
right_motor.percent_output(0)
```

### Example 5: Emergency Stop

```python
from SparkCAN import SparkBus
import time

bus = SparkBus(channel="can0", bustype='socketcan', bitrate=1000000)
motor = bus.init_controller(1)
time.sleep(1)

# Start motor
motor.percent_output(0.5)
time.sleep(1)

# Emergency stop by disabling heartbeat
bus.disable_heartbeat()
print("Emergency stop - heartbeat disabled")

# Wait and re-enable
time.sleep(2)
bus.enable_heartbeat()
print("Heartbeat re-enabled")

# Motor can be controlled again
motor.percent_output(0.3)
time.sleep(1)
motor.percent_output(0)
```

### Example 6: Using in ROS Node (from SparkCAN_Drive_Train.py)

```python
#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float64
from SparkCAN import SparkBus

# Initialize SparkBus
sparkBus = SparkBus(channel="can0", bustype='socketcan', bitrate=1000000)

# Initialize controllers for 6-wheel drive
wheels = [sparkBus.init_controller(i) for i in range(1, 7)]

# Scale factor for velocity
velocity_scale = 24.0  # 1.2 * 20

def drive_callback(data):
    """Callback for drive commands"""
    # data contains desired velocities for each wheel
    for i, wheel in enumerate(wheels):
        # Apply velocity command with scaling
        wheel.velocity_output(data.velocities[i] * velocity_scale)

def main():
    rospy.init_node('sparkcan_driver')
    rospy.Subscriber('drive_cmd', DriveCmd, drive_callback, queue_size=10)
    
    # Publish feedback at 30 Hz
    rate = rospy.Rate(30)
    while not rospy.is_shutdown():
        # Read and publish wheel velocities
        velocities = [wheel.velocity for wheel in wheels]
        # ... publish velocities ...
        rate.sleep()

if __name__ == '__main__':
    main()
```

---

## Best Practices

### 1. Initialization
- Always wait 1 second after initializing controllers before sending commands
- Initialize all controllers at startup before entering control loops

### 2. Heartbeat Management
- Keep heartbeat enabled during normal operation
- Only disable heartbeat for emergency stops or testing
- Remember to re-enable heartbeat after disabling

### 3. Power Levels
- **CRITICAL**: Enable ramping on controllers if using more than 50% power
- Start with low power levels (10-20%) when testing
- Gradually increase power while monitoring motor response

### 4. Feedback Monitoring
- Always monitor feedback (velocity/position) when using closed-loop control
- Check that feedback values are reasonable before trusting them
- Handle cases where feedback might be zero or invalid during initialization

### 5. Control Modes
- Use `percent_output()` for simple open-loop control
- Use `velocity_output()` for speed control (wheels, fans)
- Use `position_output()` for precise positioning (steering, arms)

### 6. Multiple Controllers
- Use unique CAN IDs for each controller (1-63)
- Initialize all controllers from a single SparkBus object
- Consider direction and scaling differences between controllers

### 7. Error Handling
- The library catches CAN errors and prints them
- Monitor console output for CAN communication errors
- Check physical CAN bus connections if messages fail to send

### 8. Thread Safety
- The library uses background threads for heartbeat and monitoring
- Controller methods are thread-safe for sending commands
- Feedback properties can be read from any thread

### 9. Performance
- Heartbeat runs at 50 Hz (every 20ms)
- Don't send commands faster than necessary (30-50 Hz is typical)
- Feedback is updated continuously by the monitor thread

### 10. Resource Cleanup
- Controllers will stop when heartbeat stops
- Python's garbage collector will clean up resources
- For clean shutdown, consider calling `disable_heartbeat()` before exit
