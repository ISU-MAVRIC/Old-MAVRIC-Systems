# MAVRIC SparkMax ESC Library

A library for controlling SparkMax Electronic Speed Controllers using python and a CAN Bus.

## IMPORTANT NOTE
*Motor controllers must have ramping enabled if running at more than 50% power, otherwise the motor will try to instantly go to the power level and will stutter.*

## Documentation

- **[Complete Tutorial](TUTORIAL.md)** - Comprehensive guide covering all classes and methods
- **[Limitations](#current-limitations)** - Known limitations and workarounds

## Dependencies

- Python 3 (Not tested on 2.7)
- python-can (https://python-can.readthedocs.io/en/master/)



# Example Control and Encoder Feedback Code

```python
from SparkCAN import SparkBus
import time

#Instantiate SparkBus object
bus = SparkBus(channel="can0", bustype='socketcan', bitrate=1000000)
#Create a new controller with CAN id 1
sparkESC = bus.init_controller(1)
time.sleep(1)
#Set motor to 50% power
sparkESC.percent_output(.5) #50%
#Prints the velocity 10 times, you should be able to see it ramp up as the motor gets up to speed.
for i in range(10):
    print(sparkESC.velocity)
    time.sleep(0.001)
#wait 5 seconds
time.sleep(5)
#Set motor to 0% power
sparkESC.percent_output(0)
```

---

## Current Limitations

### 1. Unimplemented Methods

**Controller.enable() and Controller.disable()**
- **Status**: These methods exist but are not implemented (contain only `pass` statements)
- **Impact**: Cannot explicitly enable/disable individual controllers via software commands
- **Workaround**: Controllers are enabled/disabled via the heartbeat mechanism
  - Use `bus.enable_heartbeat()` and `bus.disable_heartbeat()` to control all controllers
  - Controllers automatically enable when receiving heartbeat messages
  - Controllers automatically disable after heartbeat timeout (~100ms)
- **Use Case**: Emergency stop can be achieved by calling `bus.disable_heartbeat()`

### 2. Limited Status Message Support

**Only Two Status Messages Decoded**
- **Status**: The library only decodes two status message types:
  - 0x61: Velocity, plus additional status bytes (applied output, faults, sticky faults)
  - 0x62: Position feedback
  - 0x60, 0x63, 0x64: Set to `None`, not decoded
- **Impact**: 
  - No access to current draw/amperage information
  - No access to temperature readings
  - No access to voltage information
  - No access to detailed fault information
  - Applied output, faults, and sticky faults from 0x61 are decoded but not exposed
- **Workaround**: 
  - Monitor motor behavior for signs of overheating or current limits
  - Use external sensors if temperature/current monitoring is critical
  - Future enhancement: Add Status objects for 0x60, 0x63, 0x64 and expose fault data

### 3. Ramping Requirement

**High Power Operation Requires Ramping**
- **Status**: The SparkMax controllers require ramping to be enabled for smooth operation above 50% power
- **Impact**: Motors will stutter and potentially damage themselves if ramping is not enabled
- **Workaround**: 
  - Enable ramping on the SparkMax controller firmware (using REV Hardware Client)
  - Start with low power levels (10-30%) during testing
  - Gradually increase power while monitoring motor response
- **Configuration**: Ramping must be configured on each SparkMax controller via USB using REV Hardware Client before use

### 4. No Configuration Methods

**Cannot Configure Controller Parameters**
- **Status**: The library has no methods for configuring SparkMax parameters
- **Impact**: Cannot set PID values, current limits, ramping rates, or other parameters programmatically
- **Affected Parameters**:
  - PID gains (P, I, D, F)
  - Current limits
  - Voltage compensation
  - Ramping rates
  - Encoder settings
  - Idle mode (brake/coast)
- **Workaround**: All configuration must be done via USB using REV Hardware Client before deployment
- **Best Practice**: Save configurations to SparkMax flash memory so they persist across power cycles

### 5. Limited Error Reporting

**CAN Errors Only Printed**
- **Status**: CAN communication errors are caught and printed but not raised as exceptions
- **Impact**: 
  - Application continues running even if CAN communication fails
  - No programmatic way to detect communication failures
  - Silent failures possible if console output is not monitored
- **Workaround**: 
  - Monitor console output for error messages
  - Implement watchdog timers for critical operations
  - Check feedback values for reasonable ranges to detect communication issues
- **Example Error**: "Message not sent" or python-can CanError messages

### 6. No Controller Discovery

**Manual CAN ID Management Required**
- **Status**: No method to automatically discover controllers on the bus
- **Impact**: Must manually track and specify CAN IDs for each controller
- **Workaround**: 
  - Maintain documentation of CAN ID assignments
  - Use consistent ID numbering scheme (e.g., 1-6 for wheels, 7-10 for steering)
  - Label physical controllers with their CAN IDs

### 7. Fixed Heartbeat Rate

**Heartbeat Rate Not Configurable**
- **Status**: Heartbeat messages are sent at a fixed 50 Hz rate (every 20ms)
- **Impact**: Cannot adjust heartbeat rate for different applications or testing
- **Workaround**: The default 50 Hz rate works for most applications
- **Note**: Heartbeat rate is set in `_heartbeat_runnable()` method (`time.sleep(.02)`)

### 8. No Bus Statistics or Diagnostics

**No Built-in Diagnostics**
- **Status**: No methods to query bus health, message rates, or communication statistics
- **Impact**: Difficult to diagnose intermittent communication issues
- **Workaround**: 
  - Use external CAN bus analysis tools (e.g., `candump`, `cansniffer`)
  - Implement application-level monitoring of feedback update rates
  - Check for stale data by tracking last update timestamps

### 9. Thread Management

**Background Threads Always Running**
- **Status**: Heartbeat and monitor threads start automatically and run as daemon threads
- **Impact**: 
  - Threads continue until program exits
  - No clean shutdown method provided
  - May interfere with clean application shutdown
- **Workaround**: 
  - Daemon threads will automatically terminate when main program exits
  - Call `disable_heartbeat()` before exit to stop motor controllers
  - Python's garbage collector will clean up resources

### 10. Limited Data Type Support

**Only Three Data Types Supported in Status Messages**
- **Status**: Status decoder only supports `'float'`, `'int'`, and `'uint'` types
- **Impact**: Cannot decode other data types without code modification
- **Workaround**: The supported types cover most use cases
- **Note**: Uses little-endian byte order for all types

### 11. No Timeout Detection

**No Detection of Stale Feedback Data**
- **Status**: No built-in mechanism to detect if feedback data is stale or not updating
- **Impact**: Application may use old position/velocity data if controller stops responding
- **Workaround**: 
  - Implement application-level timeout checking
  - Monitor feedback update rates
  - Add timestamp tracking to Status objects if needed
  - Example:
    ```python
    last_velocity = motor.velocity
    time.sleep(0.1)
    if motor.velocity == last_velocity:
        print("Warning: Velocity feedback may be stale")
    ```

### 12. No Synchronous Operations

**All Commands Are Fire-and-Forget**
- **Status**: No way to confirm that a command was received and executed by the controller
- **Impact**: Cannot verify command execution without monitoring feedback
- **Workaround**: 
  - Monitor feedback (velocity/position) to confirm expected behavior
  - Implement application-level acknowledgment using feedback values
  - Add delays after critical commands

## Recommendations for Future Development

1. **Implement enable/disable methods**: Add explicit enable/disable CAN commands
2. **Expand status message support**: Decode all available status messages (0x60, 0x63, 0x64)
3. **Add configuration API**: Allow programmatic parameter configuration
4. **Improve error handling**: Raise exceptions for critical errors, add error callbacks
5. **Add diagnostics**: Implement bus health monitoring and statistics
6. **Add controller discovery**: Implement automatic scanning for controllers on bus
7. **Expose fault data**: Make fault and sticky fault information accessible
8. **Add timeout detection**: Track message timestamps and detect stale data
9. **Add command confirmation**: Implement acknowledgment mechanism using feedback
10. **Make heartbeat configurable**: Allow adjustment of heartbeat rate

## Known Working Configurations

- **CAN Interface**: socketcan on Linux (can0)
- **Bitrate**: 1000000 (1 Mbps)
- **Python Version**: Python 3.6+
- **SparkMax Firmware**: Tested with firmware versions 1.5.x - 1.6.x
- **Use Cases**: 
  - Rover drive systems (6-wheel drive with 4-wheel steering)
  - Robotic arms (5-axis control)
  - Science instruments (drills, actuators)

## Troubleshooting

### Motors Not Responding
- Check that heartbeat is enabled: `bus.enable_heartbeat()`
- Verify CAN bus physical connections
- Check CAN interface is up: `ip link show can0`
- Verify controller CAN IDs match initialized IDs

### Feedback Always Zero
- Check that SparkMax controllers are powered on
- Verify encoders are connected to SparkMax
- Allow time for initialization (1 second after `init_controller()`)
- Check console for CAN errors

### Motors Stuttering at High Power
- Enable ramping on SparkMax controllers using REV Hardware Client
- Reduce power level below 50%
- Check power supply voltage and current capacity