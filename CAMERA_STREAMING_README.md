# Camera Streaming README

Quick reference guide for MAVRIC rover camera systems.

## Quick Start

### Launch All Cameras
```bash
roslaunch mavric Cameras.launch
```

### Access Camera Streams

**HTTP Cameras:**
- Arm Camera: http://192.168.1.10:8097/?action=stream
- RealSense Camera: http://192.168.1.10:8098/?action=stream

**RTSP Camera (PTZ Mast):**
- Stream URL: `rtsp://admin:mavric-camera@192.168.1.64:554/out.h264`
- View in VLC: Media > Open Network Stream > paste URL

## Camera Systems Overview

| Camera | Type | Port | Stream Type | Control |
|--------|------|------|-------------|---------|
| Arm Camera | USB (UVC) | 8097 | HTTP/MJPG | Fixed |
| RealSense | USB (UVC) | 8098 | HTTP/MJPG | Fixed |
| Mast PTZ | Network (ONVIF) | 554 | RTSP | Pan/Tilt/Zoom |

## Configuration Files

- **Launch File**: `src/mavric/launch/Cameras.launch`
- **HTTP Streaming**: `src/mavric/src/HTTP_Cam.py`
- **PTZ Control**: `src/mavric/src/PTZ_Control.py`
- **Message Definition**: `src/mavric/msg/Cam.msg`

## PTZ Camera Control

### ROS Topics

- **Command Topic**: `/Mast` (mavric/Cam)
- **Feedback Topic**: `/Mast_Feedback` (mavric/Cam)

### Control Camera Position

```bash
# Center position
rostopic pub /Mast mavric/Cam "x: 0.0
y: 0.0"

# Pan right, tilt up
rostopic pub /Mast mavric/Cam "x: 0.5
y: 0.5"

# View current position
rostopic echo /Mast_Feedback
```

### Coordinate System
- **x (pan)**: -1.0 (left) to 1.0 (right)
- **y (tilt)**: -1.0 (down) to 1.0 (up)

## Adding a New Camera

### 1. Connect Hardware
- USB camera: Plug into available USB port
- Network camera: Connect to rover network

### 2. Find Device
```bash
# For USB cameras
ls -l /dev/video*
v4l2-ctl --list-devices
```

### 3. Add to Launch File

Edit `src/mavric/launch/Cameras.launch`:
```xml
<node name='new_camera' pkg='mavric' type='HTTP_Cam.py'>
    <param name="resolution" value="1280x720"/>
    <param name="frame_rate" value="30"/>
    <param name="port" value="8099"/>
    <param name="video_device" value="2"/>
</node>
```

**Important**: Use unique port number and node name!

## Network Setup

### IP Addresses
- Rover: `192.168.1.10`
- PTZ Camera: `192.168.1.64`

### Port Assignments
- 8097: Arm Camera
- 8098: RealSense Camera
- 80: PTZ ONVIF Control
- 554: PTZ RTSP Stream

## Common Commands

```bash
# List video devices
ls -l /dev/video*
v4l2-ctl --list-devices

# Check camera capabilities
v4l2-ctl -d /dev/video0 --list-formats-ext

# List ROS nodes
rosnode list | grep Camera

# Kill MJPG streamer
pkill -f mjpg_streamer

# Test RTSP stream
vlc rtsp://admin:mavric-camera@192.168.1.64:554/out.h264
ffplay rtsp://admin:mavric-camera@192.168.1.64:554/out.h264

# Monitor ROS topics
rostopic list
rostopic echo /Mast_Feedback
rostopic hz /Mast_Feedback
```

## Troubleshooting Quick Fixes

### Camera not found
```bash
lsusb                          # List USB devices
ls -l /dev/video*              # List video devices
sudo usermod -a -G video $USER # Add user to video group
```

### Port already in use
```bash
pkill -f mjpg_streamer                  # Kill existing streams
sudo netstat -tulpn | grep 8097         # Check port usage
```

### ROS node won't start
```bash
chmod +x src/mavric/src/HTTP_Cam.py     # Make executable
source devel/setup.bash                 # Source workspace
rosnode list                            # Check running nodes
```

### No video/poor quality
- Check camera connections (USB, network)
- Reduce resolution or frame rate
- Verify adequate lighting
- Check network bandwidth
- Use wired connection instead of WiFi

### PTZ camera not responding
```bash
ping 192.168.1.64                                          # Test connection
curl http://192.168.1.64                                   # Test HTTP
rostopic echo /Mast                                        # Check commands
rosnode info /Camera/mast                                  # Check node status
```

## Python Examples

### Read from HTTP Stream
```python
import cv2

# Open stream
cap = cv2.VideoCapture('http://192.168.1.10:8097/?action=stream')

while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Read from RTSP Stream
```python
from imutils.video import VideoStream
import time

vs = VideoStream('rtsp://admin:mavric-camera@192.168.1.64:554/out.h264').start()
time.sleep(2.0)  # Allow stream to initialize

frame = vs.read()
# Process frame...

vs.stop()
```

### Control PTZ Camera
```python
import rospy
from mavric.msg import Cam

rospy.init_node('camera_control')
pub = rospy.Publisher('Mast', Cam, queue_size=10)
rate = rospy.Rate(1)

# Move camera
command = Cam()
command.x = 0.5  # Pan right
command.y = 0.3  # Tilt up
pub.publish(command)
rate.sleep()
```

## Dependencies

### System Packages
```bash
# MJPG-Streamer (for HTTP streaming)
sudo apt-get install cmake libjpeg-dev

# V4L utilities
sudo apt-get install v4l-utils

# VLC (for viewing streams)
sudo apt-get install vlc
```

### Python Packages
```bash
# ONVIF support (for PTZ camera)
pip3 install onvif-zeep

# Computer vision (if needed)
pip3 install opencv-python imutils
```

### ROS Packages
```bash
# Standard ROS installation includes necessary packages
# Ensure your workspace is built:
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

## Advanced Features

### Panoramic Capture
```bash
# Capture and stitch panorama
rosrun mavric Pano_Capture.py

# Output location
~/MAVRIC-Systems/src/mavric/src/PTZ_Control/PTZ_Photos/FINAL.jpg
```

### Computer Vision Integration
See `src/mavric/src/Autonomous/ArucoClass.py` for example of integrating camera streams with OpenCV for autonomous operations.

## Configuration Parameters

### HTTP Camera (MJPG-Streamer)
- `resolution`: "640x480", "1280x720", "1920x1080"
- `frame_rate`: "15", "30", "60"
- `port`: Unique HTTP port (e.g., "8097")
- `video_device`: Device number (e.g., "0" for /dev/video0)

### PTZ Camera (ONVIF)
Configured in `src/mavric/src/PTZ_Control.py`:
- IP: 192.168.1.64
- Port: 80 (ONVIF), 554 (RTSP)
- Credentials: admin / mavric-camera

## Performance Tips

1. **Resolution**: Use lower resolution for better performance
   - 640x480: Low bandwidth, fast
   - 1280x720: Balanced
   - 1920x1080: High quality, high bandwidth

2. **Frame Rate**: Adjust based on needs
   - 15 FPS: Acceptable for most tasks
   - 30 FPS: Smooth video
   - 60 FPS: Very smooth, requires more bandwidth

3. **Network**: 
   - Use wired Ethernet when possible
   - Minimize WiFi interference
   - Keep rover and base station close

4. **USB Cameras**:
   - Use USB 3.0 ports for high-res cameras
   - Avoid USB hubs when possible
   - Check `lsusb -t` to see USB tree

## Security Notes

- **Default credentials are in code** - Change for production use
- **Cameras accessible on local network** - Ensure network security
- **No encryption** - Do not use over untrusted networks
- **Update passwords** in `PTZ_Control.py` and camera settings

## Documentation

For detailed information, see:
- **Full Tutorial**: `CAMERA_STREAMING_TUTORIAL.md`
- **Code Documentation**: Comments in source files
- **ROS Wiki**: http://wiki.ros.org
- **ONVIF Library**: https://github.com/FalkTannhaeuser/python-onvif-zeep
- **MJPG-Streamer**: https://github.com/jacksonliam/mjpg-streamer

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review full tutorial in `CAMERA_STREAMING_TUTORIAL.md`
3. Check code comments in source files
4. Contact Systems Team Lead

## Quick Reference Card

```
=== MAVRIC Camera Systems Quick Reference ===

START:
  roslaunch mavric Cameras.launch

URLS:
  Arm:      http://192.168.1.10:8097/?action=stream
  RealSense: http://192.168.1.10:8098/?action=stream
  PTZ:      rtsp://admin:mavric-camera@192.168.1.64:554/out.h264

CONTROL PTZ:
  rostopic pub /Mast mavric/Cam "x: 0.0
  y: 0.0"

DEBUG:
  rosnode list
  rostopic list
  rostopic echo /Mast_Feedback
  ls -l /dev/video*
  
STOP:
  Ctrl+C (in launch terminal)
  rosnode kill /Camera/arm_camera1
  pkill -f mjpg_streamer
```

---

**Last Updated**: 2024
**Repository**: ISU-MAVRIC/Old-MAVRIC-Systems
**Note**: This is legacy documentation for the old ROS 1 system. See new repository for ROS 2 version.
