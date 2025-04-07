import auto_globals

from StateMachine import State

class Idle(State):
    def __init__(self, stateMachine):
        self._stateMachine = stateMachine
    
    def enter(self):
        auto_globals.drive_pub.publish(0, 0, 0, 0, 0, 0)
        auto_globals.steer_pub.publish(0, 0, 0, 0)

    def run(self):
        auto_globals.debug_pub.publish("en, waypoints>0, gps, imu, gps timeout")
        auto_globals.debug_pub.publish("%d, %d, %d, %d, %d" % (auto_globals.enabled, len(auto_globals.waypoints) > 0, auto_globals.good_fix, auto_globals.good_imu, auto_globals.fix_timeout))
        auto_globals.debug_pub.publish(str(auto_globals.waypoints))

    def next(self):
        #Checks for condition needed to turn
        if(auto_globals.enabled and len(auto_globals.waypoints) > 0 and auto_globals.good_fix and auto_globals.good_imu and not auto_globals.fix_timeout):
            return self._stateMachine.turnTowardWaypoint
        
        elif auto_globals.enabled and len(auto_globals.waypoints) == 0:
            return self._stateMachine.tagFinder
        
        elif auto_globals.teleop:
            return self._stateMachine.teleop

        return self._stateMachine.idle
