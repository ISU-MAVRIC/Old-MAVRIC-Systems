import auto_globals
from StateMachine import State
from ArucoClass import Aruco
from driver import Driver
from math import copysign
import time

class TagFinder(State):
    def __init__(self, stateMachine):
        self._stateMachine = stateMachine
        self.Aruco = Aruco()
        self.D = Driver()

    def get_angular_error(self):
        return (((self.desired_heading - auto_globals.heading) + 360) % 360) if (((self.desired_heading - auto_globals.heading) + 360) % 360) < 180 else -(((auto_globals.heading - self.desired_heading) + 360) % 360)

    def get_ramped_turn_speed(self):
        turn_speed = ((auto_globals.ANG_POINT_STEER_MAX - auto_globals.ANG_POINT_STEER_MIN) / 90) * abs(self.get_angular_error()) + auto_globals.ANG_POINT_STEER_MIN
        turn_speed = turn_speed if turn_speed < auto_globals.ANG_POINT_STEER_MAX else auto_globals.ANG_POINT_STEER_MAX
        return copysign(turn_speed, self.get_angular_error())

    def enter(self):
        # Put ourselves in turn mode and wait for motors to adjust
        lf, lm, lb, rf, rm, rb, lfs, lbs, rfs, rbs = self.D.v_point_steer(0)
        auto_globals.drive_pub.publish(0,0,0,0,0,0)
        auto_globals.steer_pub.publish(lfs, lbs, rfs, rbs)
        time.sleep(3)
        # get tag data in ([ID],[MARKER_CENTER],[MARKER_CORNER]) format
        frame = self.Aruco.grab_frame()
        self.detected_tags = self.Aruco.get_markers(frame)
    
    def run(self):
        if len(self.detected_tags[0]) == 0:
            # if tag is not detected, set desired heading to 15 degrees clockwise
            self.desired_heading = (auto_globals.heading + 15) % 360
            # angular error turn from turn toward waypoint 
            while abs(self.get_angular_error()) > auto_globals.ANG_ERROR_THRESHOLD and auto_globals.enabled:
                lf, lm, lb, rf, rm, rb, lfs, lbs, rfs, rbs = self.D.v_point_steer(self.get_ramped_turn_speed())
                auto_globals.drive_pub.publish(lf, lm, lb, rf, rm, rb)
                auto_globals.steer_pub.publish(lfs, lbs, rfs, rbs)
        
        # once done, stop movement
        auto_globals.drive_pub.publish(0,0,0,0,0,0)
        time.sleep(2)

    def next(self):
        frame = self.Aruco.grab_frame()
        self.detected_tags = self.Aruco.get_markers(frame)
        if not auto_globals.enabled:
            return self._stateMachine.idle
        
        elif len(self.detected_tags[0]) > 0:
            auto_globals.steer_pub.publish(0,0,0,0)
            time.sleep(2)
            return self._stateMachine.driveTowardTag
        
        return self._stateMachine.tagFinder
