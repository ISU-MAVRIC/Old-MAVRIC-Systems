#!/usr/bin/env python3

import rospy, time, cv2, os, glob, numpy as np
from imutils.video import VideoStream
from mavric.msg import Cam

commandTopic = "/Camera/Mast"
fbTopic = "/Camera/Mast_Feedback"
dir_save = "/home/mavric/MAVRIC-Systems/src/mavric/src/PTZ_Control/PTZ_Photos/"
positions = np.linspace(-0.5,0.55,12)
# positions = [-0.5, -0.25, 0, 0.25, 0.5]
ylevel = 0.3 #0.518222
X = 0
Y = 0

vs = VideoStream('rtsp://admin:mavric-camera@192.168.1.64:554/out.h264').start()

def pos_fb(data):
    global X,Y
    X = data.x
    Y = data.y

rospy.init_node("Panoramic")
command = rospy.Publisher(commandTopic, Cam, queue_size=10)
fb = rospy.Subscriber(fbTopic, Cam, pos_fb)
rate = rospy.Rate(1)
time.sleep(1)

def capture():
    global positions
    lastPos = [X,Y]
    print("Capturing Photos")
    os.chdir(dir_save)
    for file in glob.glob("*.jpg"):
        os.remove(file)
    n = 0
    for pos in positions:
        request = Cam(pos,ylevel)
        command.publish(request)
        time.sleep(4)
        frame = vs.read()
        cv2.imwrite(dir_save + str(n) + ".jpg", frame)
        n = n + 1
        
    command.publish(Cam(lastPos[0],lastPos[1]))
    print("Finished Captures")

def stitcher():
    print("Stitching Photos")
    os.chdir(dir_save)
    imgs = []
    usedFiles = []
    for file in sorted(glob.glob("*.jpg")):
        usedFiles.append(file)
        imgs.append(cv2.imread(file))
    print(usedFiles)
    stitch = cv2.Stitcher.create(mode=cv2.Stitcher_PANORAMA)
    (status,output) = stitch.stitch(imgs)
    print("Stitching status: ", status)
    height, width, layers = output.shape
    output = cv2.resize(output, (round(width/5),height),interpolation=cv2.INTER_AREA)
    cv2.imwrite(dir_save + "FINAL.jpg", output)
    print("Finished Stitching")

if __name__ == '__main__':
    try:
        capture()
        vs.stop()
        if not rospy.is_shutdown():
            stitcher()

    except rospy.ROSInterruptException:
        vs.stop()
        print("Quitting")
        pass