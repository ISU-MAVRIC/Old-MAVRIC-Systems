import auto_globals
from geographiclib.geodesic import Geodesic
from math import copysign
import time

from driver import Driver

from StateMachine import State



#On inital trek to a waypoint, turn twords the waypoint, then advance the state
class TurnTowardWaypoint(State):
    def __init__(self, stateMachine):
        self._stateMachine = stateMachine
        self.D = Driver()
    
    def get_angular_error(self):
        return (((self.desired_heading - auto_globals.heading) + 360) % 360) if (((self.desired_heading - auto_globals.heading) + 360) % 360) < 180 else -(((auto_globals.heading - self.desired_heading) + 360) % 360)


    def get_ramped_turn_speed(self):
        turn_speed = ((auto_globals.ANG_POINT_STEER_MAX - auto_globals.ANG_POINT_STEER_MIN) / 90) * abs(self.get_angular_error()) + auto_globals.ANG_POINT_STEER_MIN
        turn_speed = turn_speed if turn_speed < auto_globals.ANG_POINT_STEER_MAX else auto_globals.ANG_POINT_STEER_MAX
        return copysign(turn_speed, self.get_angular_error())
    
    def enter(self):
        self.angular_error = auto_globals.ANG_ERROR_THRESHOLD * 2   #arbitrary, default
        lf, lm, lb, rf, rm, rb, lfs, lbs, rfs, rbs = self.D.v_point_steer(0)
        auto_globals.drive_pub.publish(0,0,0,0,0,0)
        auto_globals.steer_pub.publish(lfs, lbs, rfs, rbs)
        time.sleep(3)

    def run(self):
        auto_globals.prev_fix_time = auto_globals.fix_time  #update in gps_cb

        #set first waypoint in array as target
        tgt = [0, 0]
        tgt[0] = auto_globals.waypoints[0][0]
        tgt[1] = auto_globals.waypoints[0][1]

        #capture position in case it changes later
        pos = auto_globals.position

        #solve the geodesic problem corresponding to these lat-lon values
        #   assumes WGS-84 ellipsoid model
        geod = Geodesic.WGS84.Inverse(pos[0], pos[1], tgt[0], tgt[1])

        self.desired_heading = geod['azi1']

        start_time = time.time()
        auto_globals.debug_pub.publish(str(tgt))
        auto_globals.debug_pub.publish(str(pos))
        auto_globals.debug_pub.publish(str(geod))


        while abs(self.get_angular_error()) > auto_globals.ANG_ERROR_THRESHOLD and auto_globals.enabled:
            auto_globals.debug_pub.publish(str(self.get_ramped_turn_speed()))
            lf, lm, lb, rf, rm, rb, lfs, lbs, rfs, rbs = self.D.v_point_steer(self.get_ramped_turn_speed())
            auto_globals.debug_pub.publish(str(self.get_angular_error()))
            auto_globals.debug_pub.publish("a"+str(self.desired_heading))
            auto_globals.drive_pub.publish(lf, lm, lb, rf, rm, rb)
            auto_globals.steer_pub.publish(lfs, lbs, rfs, rbs)
        auto_globals.drive_pub.publish(0,0,0,0,0,0)
        auto_globals.steer_pub.publish(0,0,0,0)

    def next(self):
        if(not auto_globals.enabled or not auto_globals.good_fix or auto_globals.fix_timeout):
            return self._stateMachine.idle

        if(abs(self.get_angular_error()) < auto_globals.ANG_ERROR_THRESHOLD):
            auto_globals.drive_pub.publish(0,0,0,0,0,0)
            time.sleep(2)
            auto_globals.steer_pub.publish(0,0,0,0)
            time.sleep(2)
            auto_globals.debug_pub.publish("Exiting TurnTowardWaypointState.py")
            return self._stateMachine.driveTowardWaypoint

        return self._stateMachine.turnTowardWaypoint
