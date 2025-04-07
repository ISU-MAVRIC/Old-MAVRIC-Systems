import auto_globals
from StateMachine import State
import time

class ReachedWaypoint(State):
    def __init__(self, stateMachine):
        self._stateMachine = stateMachine
    
    def enter(self):
        auto_globals.drive_pub.publish(0, 0, 0, 0, 0, 0)
        auto_globals.steer_pub.publish(0, 0, 0, 0)


    def run(self):
        auto_globals.debug_pub.publish("Waypoint Reached!!")
        pass

    def next(self):
	    # Continue with paths
        if(len(auto_globals.waypoints) > 1):
            auto_globals.waypoints.pop(0)
            return self._stateMachine.turnTowardWaypoint

        # at last waypoint, use tagfinder
        elif(len(auto_globals.waypoints) > 0):
            auto_globals.waypoints.pop(0)
            auto_globals.reached_pub.publish(True)
            return self._stateMachine.tagFinder
        else:
            auto_globals.reached_pub.publish(True)
            return self._stateMachine.idle