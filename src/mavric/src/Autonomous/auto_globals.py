#global constants
LIN_ERROR_THRESHOLD = 2     #arbitrary, meters
ANG_ERROR_THRESHOLD = 5    #arbitrary, degrees
ANG_POINT_STEER_MAX = 20 #between 1-100 (inclusive)
ANG_POINT_STEER_MIN = 2 
ANG_POINT_STEER_TIMEOUT = 10000 #max ms until Turn state exit
UPDATE_INTERVAL = 1
FIX_TIMEOUT_THRESHOLD = UPDATE_INTERVAL * 5

#control flags
enabled = False
good_fix = False
good_imu = True
fix_timeout = False   #unnecessary?
teleop = False

#location data
position = [0, 0]
prev_position = [0, 0]
waypoints = []

#IMU data
heading = 0

prev_angular_error = ANG_ERROR_THRESHOLD * 2
prev_linear_error = LIN_ERROR_THRESHOLD * 2

#GPS timeout data
fix_time = 0
prev_fix_time = 0

#ROS params
Scale = 0
Rover_Width = 0
Rover_MinTurnRadius = 0

#ROS publishers (initialized in main)
drive_pub = None
steer_pub = None
debug_pub = None
indicator_pub = None
state_pub = None
waypoint_pub = None
reached_pub = None
