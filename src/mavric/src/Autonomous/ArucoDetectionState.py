#!/usr/bin/env python3

import auto_globals
import rospy
import cv2
import threading
import time
from mavric.msg import Drivetrain, Steertrain
from std_msgs.msg import Bool
from driver import Driver
from StateMachine import State

class ArucoDetection(State):
    
    def __init__(self, stateMachine):
        self._stateMachine = stateMachine
        self.enable = False
        self.driveSpeed = 7
        self.lTheta = -45
        self.rTheta = 12
        self.driveMath = Driver()
        
        
    def enter(self):
        auto_globals.drive_pub.publish(0, 0, 0, 0, 0, 0)
        auto_globals.steer_pub.publish(0, 0, 0, 0)


    def enable_cb(self, data):
        global enable
        if data.data:
            self.enable = True
        else:
            self.enable = False


    def get_markers_from_frame(self, frame, detector):
        markerLocations = []
        markerIds = []
        markerCorners= []
        (corners, ids, rejected) = detector.detectMarkers(frame)
        if (len(corners) > 0):
            ids = ids.flatten()
            for (markerCorner, markerID) in zip(corners, ids):
                corners = markerCorner.reshape((4, 2))
                (topLeft, topRight, bottomRight, bottomLeft) = corners
                bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                topLeft = (int(topLeft[0]), int(topLeft[1]))

                # compute and draw the center (x, y)-coordinates of the
                # ArUco marker
                cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                markerLocations.append((cX, cY))
                markerIds.append(markerID)
                markerCorners.append((topLeft, bottomRight))
        return (markerIds, markerLocations, markerCorners)

    def run(self):
        vs2 = cv2.VideoCapture('rtsp://admin:mavric-camera@192.168.1.64:554/out.h264')
        time.sleep(1)
        lastFix = 0
        currentFix = 5
        drive = 0
        steer = 0
        fault = 0

        if __name__ == "__main__":
            try:
                rospy.init_node("Aruco")
                drive_pub = rospy.Publisher("/Drive/Drive_Command", Drivetrain, queue_size=10)
                steer_pub = rospy.Publisher("/Drive/Steer_Command", Steertrain, queue_size=10)
                enable_sub = rospy.Subscriber("/Auto/Enable", Bool, self.enable_cb)
                thread = threading.Thread(target=self.run)
                thread.start()
            except rospy.ROSInterruptException:
                thread._stop()
                return self._stateMachine.idle

        while True:
            ret, frame2 = vs2.read()
            time.sleep(0.01)

            if not ret:
                break

            markers2 = self.get_markers_from_frame(frame2)
            angles = []

            for index, ID in enumerate(markers2[0]):
                angles.append((float(markers2[1][index][0] - 973) / 973) * 48.9)
                frame2 = cv2.rectangle(frame2, markers2[2][index][0], markers2[2][index][1], (255, 0, 0), 2)
                frame2 = cv2.rectangle(frame2, markers2[2][index][0], (markers2[2][index][0][0] + 100, markers2[2][index][0][1] - 20), (0, 0, 0), -1)
                frame2 = cv2.putText(frame2, "ID: " + str(ID) + " Theta: " + str(int(angles[index])), markers2[2][index][0], cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 255, 255), 1, cv2.LINE_AA)

            if len(angles) > 0:
                if fault <= 0:
                    self.lastFix = time.perf_counter()
                    fault = 0
                    steer = 100 / (self.rTheta - self.lTheta) * (angles[0] - (self.rTheta + self.lTheta) / 2)
                    drive = self.driveSpeed
                fault = fault - 1
            else:
                self.currentFix = time.perf_counter()
                fault = fault + 1
                if fault >= 5:
                    if self.currentFix - self.lastFix > 3:
                        steer = 0
                        drive = 0
                    elif currentFix - lastFix > 1:
                        steer = 0
                    fault = 5

            if self.enable:
                lf, lm, lb, rf, rm, rb, lfs, lbs, rfs, rbs = self.driveMath.v_car_steer(drive, steer)
                self.drive_pub.publish(lf, lm, lb, rf, rm, rb)
                self.steer_pub.publish(lfs, lbs, rfs, rbs)
            else:
                self.drive_pub.publish(0, 0, 0, 0, 0, 0)
                self.steer_pub.publish(0, 0, 0, 0)
        return (self.currentFix, self.lastFix)
        

    def next(self):
        if self.currentFix - self.lastFix > 3:
            return self._stateMachine.idle
        else:
            return self.stateMachine.ArucoDetection