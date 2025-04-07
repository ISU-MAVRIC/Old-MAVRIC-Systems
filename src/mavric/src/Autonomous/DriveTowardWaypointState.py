import auto_globals, time
from geographiclib.geodesic import Geodesic
from math import copysign
import math as m

from StateMachine import State
from driver import Driver

class DriveTowardWaypoint(State):
    def __init__(self, stateMachine):
        self._stateMachine = stateMachine
        self.DriveLib = Driver()

    def enter(self):
        self.linear_error = auto_globals.LIN_ERROR_THRESHOLD * 2

    def run(self):
        auto_globals.prev_fix_time = auto_globals.fix_time

        #set first waypoint in array as target
        tgt = [0, 0]
        tgt[0] = auto_globals.waypoints[0][0]
        tgt[1] = auto_globals.waypoints[0][1]

        #capture position in case it changes later
        pos = auto_globals.position

        #https://geographiclib.sourceforge.io/html/python/code.html#geographiclib.geodesic.Geodesic.Inverse
        #The inverse function returns an array of data regarding the soltion of the geodesic problem, more can be read about it above
        #solve the geodesic problem corresponding to these lat-lon values
        #   assumes WGS-84 ellipsoid model
        geod = Geodesic.WGS84.Inverse(pos[0], pos[1], tgt[0], tgt[1])

        #get linear error in meters
        self.linear_error = geod['s12']

        #todo, investigate what needs to happen here if we are messing with the heading this early
        #get angular error in CW degrees (account for 360 rollover)
        self.angular_error = (((geod['azi1'] - auto_globals.heading) + 360) % 360) if (((geod['azi1'] - auto_globals.heading) + 360) % 360) < 180 else -(((auto_globals.heading - geod['azi1']) + 360) % 360)


        #Check speed based on distance, probably some hard coded number
        #get values from some functions that do checking based on the offsets
        #remaining distance in meters
        decel_dist = 100
        
        rem_dist = self.linear_error
        turn_error = self.angular_error
        
        
        
        #Calculate linear velocity
        #Based on linear offset, output scaled max velocity        
        
        
        #shifts velocity by c, on the x axis
        #directly correlates by 1 meter
        #this could also help if rover doesn't seem to be slowing enough before a stop
        c = 7
        
        #controls the top end of the curve. top velocity, presumably 0 -> 100
        #TODO check range, starting with 40 percent power, if 100 is max velocity
        b = 40
        
        #r controls when the deccel starts, 0.75 is around 10 - 15m
        #0.3 is around 20m
        #note that this literally stretches the curve, the funciton then may need to be shifted
        r = 0.75
        
        #do speed input based on remaining distance, use r to adjust when the algo kicks in
        if rem_dist < 1000:
            velocity = (b * m.exp(r * rem_dist)) / ( m.exp(c * r) + m.exp(r * rem_dist))
        else:
            velocity = b

        #Calculate wheel angle
        #Based on angular offset, turning angle based severity of offset
        
        #TODO should the wheel turn angle just literally be the offset? or the opposite of the offset?
        #TODO, do we need to ramp this value somehow, or scale it base on the offset?
        wheel_angle = turn_error*1.1
        
        
        #given some steering data, return vector of motor data
        driveVals = self.DriveLib.v_car_steer(velocity, wheel_angle) #TODO implement actual function

        #publish drive data, given from DriveLib
        #publish first 6 wheel speed values    
        auto_globals.drive_pub.publish(driveVals[0], driveVals[1], driveVals[2], driveVals[3], driveVals[4], driveVals[5])
        #publish 4 wheel steer parameters
        auto_globals.steer_pub.publish(driveVals[6], driveVals[7], driveVals[8], driveVals[9])

        #TODO, update publisher data, and how it works. You need to get a publisher for steering
        #auto_globals.drive_pub.publish() #TODO
        #auto_globals.steer_pub.publish() #TODO


        #remember linear error for the next cycle
        auto_globals.prev_linear_error = self.linear_error

        auto_globals.debug_pub.publish("lin error")
        auto_globals.debug_pub.publish(str(self.linear_error))

    def next(self):
        if(auto_globals.prev_linear_error < self.linear_error):   # if the rover skips the waypoint and remaining distance starts increasing
            return self._stateMachine.turnTowardWaypoint
        
        elif(not auto_globals.enabled or not auto_globals.good_fix or auto_globals.fix_timeout):
            return self._stateMachine.idle
            
        elif(self.linear_error <= auto_globals.LIN_ERROR_THRESHOLD):
            auto_globals.drive_pub.publish(0,0,0,0,0,0)
            time.sleep(1)
            return self._stateMachine.reachedWaypoint
        else:
            return self._stateMachine.driveTowardWaypoint
