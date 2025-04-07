#!/usr/bin/env python3

#import modules
import auto_globals, rospy, json

from types import SimpleNamespace as Namespace

from std_msgs.msg import String, Bool, Float64
from geometry_msgs.msg import Vector3
from mavric.msg import Drivetrain, Steertrain, GPS

from StateMachine import StateMachine, State
from IdleState import Idle
from TurnTowardWaypointState import TurnTowardWaypoint
from DriveTowardWaypointState import DriveTowardWaypoint
from ReachedWaypointState import ReachedWaypoint
from TagFinderState import TagFinder
from DriveTowardTagState import DriveTowardTag
from TeleopState import Teleop

# ----- define state machine class -----
class AutonomousStateMachine(StateMachine):
    def __init__(self):
        StateMachine.__init__(self, AutonomousStateMachine.idle)


AutonomousStateMachine.idle = Idle(AutonomousStateMachine)
AutonomousStateMachine.turnTowardWaypoint = TurnTowardWaypoint(AutonomousStateMachine)
AutonomousStateMachine.driveTowardWaypoint = DriveTowardWaypoint(AutonomousStateMachine)
AutonomousStateMachine.reachedWaypoint = ReachedWaypoint(AutonomousStateMachine)
AutonomousStateMachine.tagFinder = TagFinder(AutonomousStateMachine)
AutonomousStateMachine.driveTowardTag = DriveTowardTag(AutonomousStateMachine)
AutonomousStateMachine.teleop = Teleop(AutonomousStateMachine)


# ----- define functions -----

def hms_to_s(h, m, s):
    # convert from hours-minutes-seconds to seconds
    return (h * 60 * 60) + (m * 60) + s

def cmd_cb(data):
    # enable/disable autonomous
    auto_globals.enabled = data.data

def waypoint_cb(data):
    recieved = json.loads(data.data, object_hook=lambda d: Namespace(**d))
    # if the data is the same (most likely from an internal repush for base station)
    if recieved != auto_globals.waypoints:
        auto_globals.waypoints = recieved
    else:
        pass

def gps_fix_cb(data):
    # auto_globals.good_fix = data.data
    auto_globals.good_fix = True

def gps_cb(data):
    auto_globals.prev_position = auto_globals.position
    auto_globals.position = [data.latitude, data.longitude]
    auto_globals.fix_time = hms_to_s(data.time_h, data.time_m, data.time_s)
    #auto_globals.heading = data.heading

def imu_cb(data):
    if auto_globals.good_imu:
        auto_globals.heading = data.z
    else:
        auto_globals.heading = data.z

def imu_cal_cb(data):
    if data.data > 0:
       auto_globals.good_imu = True
    else:
       auto_globals.good_imu = True

def teleop_cp(data):
    auto_globals.teleop = data.data


# main loop
auto = AutonomousStateMachine()


def main():
    # setup ROS node
    rospy.init_node("ANS")

    # init publishers
    auto_globals.drive_pub = rospy.Publisher("Drive_Train", Drivetrain, queue_size=10)
    auto_globals.steer_pub = rospy.Publisher("Steer_Train", Steertrain, queue_size=10)
    auto_globals.debug_pub = rospy.Publisher("Debug", String, queue_size=10)
    auto_globals.state_pub = rospy.Publisher("State", String, queue_size=10)
    auto_globals.waypoint_pub = rospy.Publisher("Waypoints", String, queue_size=10) 
    auto_globals.reached_pub = rospy.Publisher("Success", Bool, queue_size=10)
    # init Subscribers
    cmd_sub = rospy.Subscriber("Enable", Bool, cmd_cb, queue_size=10)
    way_sub = rospy.Subscriber("Waypoints", String, waypoint_cb, queue_size=10)
    gps_fix_sub = rospy.Subscriber("GPS_Fix", Bool, gps_fix_cb, queue_size=10)
    gps_sub = rospy.Subscriber("GPS", GPS, gps_cb, queue_size=10)
    imu_sub = rospy.Subscriber("FusedAngle", Vector3, imu_cb, queue_size=10)
    imu_cal_sub = rospy.Subscriber("SensorCalibrations", Float64, imu_cal_cb, queue_size=10)
    teleop_sub = rospy.Subscriber("Teleop", Bool, teleop_cp, queue_size=10)

    auto_globals.Scale = rospy.get_param("~Range", 0.5)
    auto_globals.Rover_Width = rospy.get_param("~Rover_Width", 1)
    auto_globals.Rover_MinTurnRadius = rospy.get_param("~Rover_MinTurnRadius", 2)
    
    rate = rospy.Rate(2)  # 2 Hz
    i = 0
    while not rospy.is_shutdown():
        auto.run(auto_globals.state_pub)

        # updates the base station list of waypoints. This is done once every 5 seconds to not hammer the waypoints subscriber with "useless" messages
        i = i + 1
        if i > 4:
            auto_globals.waypoint_pub.publish(json.dumps(auto_globals.waypoints))
            i = 0
        rate.sleep()


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
