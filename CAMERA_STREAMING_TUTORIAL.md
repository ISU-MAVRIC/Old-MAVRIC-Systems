# Camera Streaming Tutorial

## Overview

The MAVRIC rover system uses multiple camera streaming solutions to provide real-time video feeds for navigation, object detection, and remote operation. This tutorial covers the setup, configuration, and usage of all camera streaming systems in the rover.

## Camera Systems

The rover implements three distinct camera streaming systems:

1. **HTTP Streaming (MJPG-Streamer)** - For standard USB cameras (Arm and RealSense cameras)
2. **RTSP Streaming (PTZ Camera)** - For the ONVIF-compatible mast camera with pan-tilt-zoom control
3. **Video Processing Streams** - For autonomous operations using computer vision

---

## 1. HTTP Camera Streaming (MJPG-Streamer)

### Overview

The HTTP camera streaming system uses MJPG-Streamer to provide HTTP-based video streams from USB cameras. This is implemented in `src/mavric/src/HTTP_Cam.py`.

### Hardware Requirements

- USB camera (UVC-compatible)
- Available USB port on the rover
- Network connection to the rover

### Software Dependencies

- `mjpg-streamer` - Must be installed on the rover
- ROS (Robot Operating System)
- Python 3

### Installation

1. **Install MJPG-Streamer:**
   ```bash
   cd /home/mavric
   git clone https://github.com/jacksonliam/mjpg-streamer.git
   cd mjpg-streamer/mjpg-streamer-experimental
   make
   sudo make install
   ```

2. **Verify Installation:**
   ```bash
   mjpg_streamer --help
   ```

### Configuration

The HTTP camera system is configured through ROS parameters in the launch file (`src/mavric/launch/Cameras.launch`):

```xml
<node name='arm_camera1' pkg='mavric' type='HTTP_Cam.py'>
    <param name="resolution" value="1280x720"/>
    <param name="frame_rate" value="30"/>
    <param name="port" value="8097"/>
    <param name="video_device" value="0"/>
</node>
```

#### Parameters:

- **resolution**: Video resolution (e.g., "1280x720", "1920x1080")
- **frame_rate**: Frames per second (e.g., "30", "60")
- **port**: HTTP port for streaming (e.g., "8097", "8098")
- **video_device**: Video device number (e.g., "0" for /dev/video0)

### Finding Your Camera Device

To find which `/dev/video*` device your camera is connected to:

```bash
# List all video devices
ls -l /dev/video*

# Get detailed info about video devices
v4l2-ctl --list-devices

# Test a specific camera
v4l2-ctl -d /dev/video0 --list-formats-ext
```

### Usage

#### Starting the Camera Stream

Using ROS launch file (recommended):
```bash
roslaunch mavric Cameras.launch
```

Starting individually:
```bash
rosrun mavric HTTP_Cam.py _resolution:=1280x720 _frame_rate:=30 _port:=8097 _video_device:=0
```

#### Accessing the Stream

Once running, access the stream through:

- **Web Browser**: `http://192.168.1.10:8097/?action=stream`
- **Direct Stream URL**: `http://192.168.1.10:8097/?action=stream`
- **Snapshot**: `http://192.168.1.10:8097/?action=snapshot`

Replace `192.168.1.10` with your rover's IP address and `8097` with your configured port.

#### Stopping the Stream

The stream will automatically stop when the ROS node is terminated:
```bash
# Ctrl+C in the terminal running the launch file
# Or use:
rosnode kill /Camera/arm_camera1
```

### Multiple Camera Setup

The system supports multiple cameras simultaneously. Example from `Cameras.launch`:

```xml
<!-- Arm Camera -->
<node name='arm_camera1' pkg='mavric' type='HTTP_Cam.py'>
    <param name="port" value="8097"/>
    <param name="video_device" value="0"/>
</node>

<!-- Realsense Camera -->
<node name='realsense' pkg='mavric' type='HTTP_Cam.py'>
    <param name="port" value="8098"/>
    <param name="video_device" value="3"/>
</node>
```

**Important**: Each camera must have:
- A unique port number
- A unique node name
- The correct video device number

### Troubleshooting

#### Camera not found
```bash
# Check if camera is detected
lsusb
ls -l /dev/video*

# Check camera permissions
sudo usermod -a -G video $USER
```

#### Port already in use
```bash
# Kill existing mjpg_streamer processes
pkill -f mjpg_streamer

# Check what's using the port
sudo netstat -tulpn | grep 8097
```

#### Low frame rate or quality
- Reduce resolution in launch file
- Reduce frame rate
- Check USB bandwidth (avoid USB hubs if possible)
- Ensure adequate lighting conditions

---

## 2. PTZ Camera Control (ONVIF)

### Overview

The PTZ (Pan-Tilt-Zoom) camera system controls an ONVIF-compatible network camera with motorized pan and tilt capabilities. This is implemented in `src/mavric/src/PTZ_Control.py`.

### Hardware Requirements

- ONVIF-compatible PTZ camera (e.g., IP camera with PTZ support)
- Network connection to camera
- Camera must support RTSP streaming

### Software Dependencies

- `python-onvif-zeep` - Python ONVIF library
- ROS (Robot Operating System)
- Python 3

### Installation

1. **Install python-onvif-zeep:**
   ```bash
   pip3 install onvif-zeep
   ```

2. **Verify Camera Connection:**
   ```bash
   ping 192.168.1.64
   ```

### Camera Configuration

The PTZ camera is configured in `src/mavric/src/PTZ_Control.py`:

```python
mycam = ONVIFCamera('192.168.1.64', 80, 'admin', 'mavric-camera')
```

#### Configuration Parameters:

- **IP Address**: `192.168.1.64` (default rover mast camera)
- **Port**: `80` (HTTP port for ONVIF)
- **Username**: `admin`
- **Password**: `mavric-camera`

### RTSP Stream Access

The camera provides an RTSP stream at:
```
rtsp://admin:mavric-camera@192.168.1.64:554/out.h264
```

This stream can be accessed by:
- VLC Media Player: `Media > Open Network Stream`
- FFmpeg: `ffmpeg -i rtsp://admin:mavric-camera@192.168.1.64:554/out.h264`
- OpenCV/Python (used in autonomous code)

### ROS Topics

The PTZ control system uses custom ROS messages defined in `src/mavric/msg/Cam.msg`:

```
# camera axes
# x = pan, y = tilt
float32 x
float32 y
```

#### Subscribed Topics:

- **`/Mast`** (mavric/Cam): Commands for camera position
  - `x`: Pan position (-1.0 to 1.0, left to right)
  - `y`: Tilt position (-1.0 to 1.0, down to up)

#### Published Topics:

- **`/Mast_Feedback`** (mavric/Cam): Current camera position feedback

### Usage

#### Starting PTZ Control

Using launch file:
```bash
roslaunch mavric Cameras.launch
```

Individual node:
```bash
rosrun mavric PTZ_Control.py
```

#### Controlling Camera Position

Publish commands to the `/Mast` topic:

```bash
# Move camera to center position (x=0, y=0)
rostopic pub /Mast mavric/Cam "x: 0.0
y: 0.0"

# Pan right, tilt up (x=0.5, y=0.5)
rostopic pub /Mast mavric/Cam "x: 0.5
y: 0.5"

# Pan left, tilt down (x=-0.5, y=-0.5)
rostopic pub /Mast mavric/Cam "x: -0.5
y: -0.5"
```

#### Python Example

```python
import rospy
from mavric.msg import Cam

rospy.init_node('camera_control')
pub = rospy.Publisher('Mast', Cam, queue_size=10)
rate = rospy.Rate(1)  # 1 Hz

# Move camera to specific position
command = Cam()
command.x = 0.5   # Pan right
command.y = 0.3   # Tilt up slightly
pub.publish(command)
rate.sleep()
```

#### Monitoring Camera Position

```bash
# View current camera position
rostopic echo /Mast_Feedback

# Monitor in real-time
rostopic hz /Mast_Feedback
```

### Coordinate System

The PTZ camera uses a normalized coordinate system:

- **Pan (x-axis)**:
  - `-1.0`: Full left
  - `0.0`: Center
  - `1.0`: Full right

- **Tilt (y-axis)**:
  - `-1.0`: Full down
  - `0.0`: Center (horizontal)
  - `1.0`: Full up

### Advanced Features

#### Position Feedback Rate

The feedback is published at 2 Hz (configurable in `PTZ_Control.py`):
```python
rate = rospy.Rate(2)
```

#### Movement Interruption

The system supports movement interruption - sending a new command will stop the current movement and start a new one.

### Troubleshooting

#### Cannot connect to camera
```bash
# Verify camera is accessible
ping 192.168.1.64

# Check camera web interface
curl http://192.168.1.64

# Verify credentials
# Try accessing http://192.168.1.64 in a web browser
```

#### Camera not responding to commands
```bash
# Check if PTZ_Control node is running
rosnode list | grep PTZ

# Check topic connections
rostopic info /Mast

# Verify message is being received
rostopic echo /Mast
```

#### RTSP stream not accessible
```bash
# Test RTSP stream with VLC or ffplay
vlc rtsp://admin:mavric-camera@192.168.1.64:554/out.h264

# Or with ffplay
ffplay -rtsp_transport tcp rtsp://admin:mavric-camera@192.168.1.64:554/out.h264
```

---

## 3. Panoramic Capture System

### Overview

The panoramic capture system (`src/mavric/src/PTZ_Control/Pano_Capture.py`) automates the process of capturing multiple images with the PTZ camera and stitching them into a panoramic image.

### Features

- Automated camera positioning
- Sequential image capture
- Automatic image stitching using OpenCV
- Configurable capture positions

### Configuration

Edit the following parameters in `Pano_Capture.py`:

```python
# Directory to save photos
dir_save = "/home/mavric/MAVRIC-Systems/src/mavric/src/PTZ_Control/PTZ_Photos/"

# Number and positions of captures (12 positions from -0.5 to 0.55)
positions = np.linspace(-0.5, 0.55, 12)

# Vertical level for captures
ylevel = 0.3
```

### Usage

1. **Ensure PTZ_Control is running:**
   ```bash
   roslaunch mavric Cameras.launch
   ```

2. **Run panoramic capture:**
   ```bash
   rosrun mavric Pano_Capture.py
   ```

3. **Output:**
   - Individual images: `/home/mavric/.../PTZ_Photos/0.jpg`, `1.jpg`, etc.
   - Stitched panorama: `/home/mavric/.../PTZ_Photos/FINAL.jpg`

### Workflow

1. Camera moves to first position
2. Waits 4 seconds for camera to stabilize
3. Captures frame from RTSP stream
4. Repeats for all positions
5. Returns camera to original position
6. Stitches all images into panorama
7. Saves compressed final image

### Customization

To change the number of capture positions:
```python
# Capture fewer images (5 positions)
positions = [-0.5, -0.25, 0, 0.25, 0.5]

# Capture more images (20 positions)
positions = np.linspace(-0.5, 0.55, 20)
```

---

## 4. Computer Vision Integration

### Overview

The `ArucoClass.py` demonstrates how to integrate the camera streams into computer vision applications for autonomous operations.

### RTSP Stream in Python

Basic example using `imutils.VideoStream`:

```python
from imutils.video import VideoStream
import cv2

# Connect to RTSP stream
vs = VideoStream('rtsp://admin:mavric-camera@192.168.1.64:554/out.h264').start()

# Give stream time to initialize
time.sleep(2.0)

# Read frames
frame = vs.read()

# Process frame with OpenCV
# ... your processing code ...

# Clean up
vs.stop()
```

### Aruco Marker Detection Example

The rover uses Aruco markers for autonomous navigation. Example from `ArucoClass.py`:

```python
from imutils.video import VideoStream
import cv2
import numpy as np

class Aruco():
    def __init__(self, display=True):
        # Setup Aruco detector
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.dictionary, self.parameters)
        
        # Connect to camera stream
        self.vs = VideoStream('rtsp://admin:mavric-camera@192.168.1.64:554/out.h264').start()
        time.sleep(2.0)
    
    def detect_markers(self):
        frame = self.vs.read()
        (corners, ids, rejected) = self.detector.detectMarkers(frame)
        return corners, ids
    
    def __del__(self):
        self.vs.stop()
```

---

## Network Architecture

### IP Addresses

- **Rover (Master)**: `192.168.1.10`
- **PTZ Mast Camera**: `192.168.1.64`
- **Base Station**: Connect to rover's network

### Port Assignments

- **Arm Camera HTTP Stream**: `8097`
- **RealSense Camera HTTP Stream**: `8098`
- **PTZ Camera ONVIF**: `80`
- **PTZ Camera RTSP**: `554`

### Network Setup

1. **Connect to Rover Network:**
   - WiFi SSID: (rover-specific)
   - Ensure your device is on the same subnet (192.168.1.x)

2. **Verify Connectivity:**
   ```bash
   ping 192.168.1.10   # Rover
   ping 192.168.1.64   # PTZ Camera
   ```

---

## Integration with Base Station

The Base Station software (in `Base Station/RoverBaseStation.py`) provides a graphical interface for viewing camera streams and controlling the rover. While the base station code is separate, it accesses the same camera streams documented here.

### Base Station Camera Access

The base station can access:
- HTTP streams via web browser or HTTP client
- RTSP stream via media player integration
- PTZ control via ROS topic publishing

---

## Best Practices

### Performance Optimization

1. **Resolution**: Use appropriate resolution for your use case
   - Navigation: 640x480 or 1280x720
   - High detail tasks: 1920x1080

2. **Frame Rate**: Balance between smoothness and bandwidth
   - 15-20 FPS: Adequate for most tasks
   - 30 FPS: Smooth video, higher bandwidth

3. **Network**: Use wired Ethernet when possible for best performance

### Camera Maintenance

1. **Clean Lenses**: Regularly clean camera lenses
2. **Check Connections**: Verify USB and network connections
3. **Update Firmware**: Keep camera firmware updated
4. **Monitor Temperature**: Ensure adequate cooling

### Security

1. **Change Default Passwords**: Update camera credentials
2. **Network Isolation**: Use dedicated rover network
3. **Access Control**: Limit who can access camera streams

---

## Troubleshooting Guide

### General Issues

#### No Video Stream

1. Check camera power and connections
2. Verify network connectivity
3. Check if camera node is running: `rosnode list`
4. Review error logs: `rosnode log /Camera/arm_camera1`

#### Poor Video Quality

1. Adjust resolution and frame rate
2. Check lighting conditions
3. Verify camera focus
4. Check network bandwidth

#### High Latency

1. Reduce resolution or frame rate
2. Check network connection quality
3. Minimize WiFi interference
4. Use wired connection if possible

### ROS-Specific Issues

#### Node Won't Start

```bash
# Check ROS environment
echo $ROS_PACKAGE_PATH

# Source ROS setup
source /opt/ros/noetic/setup.bash
source /path/to/catkin_ws/devel/setup.bash

# Check node permissions
chmod +x src/mavric/src/HTTP_Cam.py
```

#### Topic Not Publishing

```bash
# List all topics
rostopic list

# Check topic info
rostopic info /Mast

# Echo topic to see messages
rostopic echo /Mast_Feedback
```

---

## Additional Resources

### Documentation Links

- **ONVIF Python Library**: https://github.com/FalkTannhaeuser/python-onvif-zeep
- **MJPG-Streamer**: https://github.com/jacksonliam/mjpg-streamer
- **ROS Camera Tutorials**: http://wiki.ros.org/camera_calibration
- **OpenCV Documentation**: https://docs.opencv.org/

### Example Code Location

- **HTTP Streaming**: `src/mavric/src/HTTP_Cam.py`
- **PTZ Control**: `src/mavric/src/PTZ_Control.py`
- **Panoramic Capture**: `src/mavric/src/PTZ_Control/Pano_Capture.py`
- **Computer Vision**: `src/mavric/src/Autonomous/ArucoClass.py`
- **Launch Files**: `src/mavric/launch/Cameras.launch`

### Camera Configuration Files

- **ROS Launch File**: `src/mavric/launch/Cameras.launch`
- **Message Definitions**: `src/mavric/msg/Cam.msg`

---

## Appendix

### Camera Specifications (Typical)

#### HTTP Cameras (USB)
- Interface: USB 2.0/3.0
- Resolution: Up to 1920x1080
- Frame Rate: 30 FPS
- Protocol: UVC (USB Video Class)

#### PTZ Camera (Network)
- Interface: Ethernet
- Resolution: Varies by model
- Pan Range: ±180° (typical)
- Tilt Range: ±90° (typical)
- Protocol: ONVIF, RTSP

### Command Reference

```bash
# Start all cameras
roslaunch mavric Cameras.launch

# Start individual camera
rosrun mavric HTTP_Cam.py _port:=8097 _video_device:=0

# Control PTZ camera
rostopic pub /Mast mavric/Cam "x: 0.0, y: 0.0"

# View camera feedback
rostopic echo /Mast_Feedback

# Kill mjpg_streamer
pkill -f mjpg_streamer

# List video devices
ls -l /dev/video*
v4l2-ctl --list-devices
```

### Camera Coordinate Reference

```
PTZ Camera Coordinate System:
        y = 1.0 (up)
           |
           |
x = -1.0 --+-- x = 1.0
 (left)    |    (right)
           |
        y = -1.0 (down)
```

---

## Conclusion

This tutorial covers the complete camera streaming infrastructure for the MAVRIC rover. The system is modular and extensible, allowing for easy addition of new cameras or modification of existing ones. For questions or issues not covered here, consult the Systems Team Lead or refer to the code comments in the source files.
