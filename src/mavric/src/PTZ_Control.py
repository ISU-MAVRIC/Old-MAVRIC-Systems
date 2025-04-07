#!/usr/bin/env python3
import rospy
from mavric.msg import Cam
from onvif import ONVIFCamera
'''
----- PTZ CONTROL -----
Author: Nathan Logston
Topics:
    Subscribers:
        Mast

This script is able to control a PTZ camera that has ONVIF protocol.
We only use this script to control the mast cam for now, so it's details are hard locked in.
If you want to change this, check the setup_move() function and the mycam variable

More documentation about this script can be found here: https://github.com/FalkTannhaeuser/python-onvif-zeep/tree/zeep
This script is essentailly a "rossified" version of this: https://github.com/FalkTannhaeuser/python-onvif-zeep/blob/zeep/examples/AbsoluteMove.py
'''

# default camera values. These work for most onvif cameras
XMAX = 1
XMIN = -1
XNOW = 0.5
YMAX = 1
YMIN = -1
YNOW = 0.5
Move = 0.1
Velocity = 1
Zoom = 0
positionrequest = None
ptz = None
active = False
ptz_configuration_options = None
media_profile = None


def setup_move():
    # create a camera instance
    mycam = ONVIFCamera('192.168.1.64', 80, 'admin', 'mavric-camera')
    # Create media service object
    media = mycam.create_media_service()

    # Create ptz service object
    global ptz , ptz_configuration_options, media_profile
    ptz = mycam.create_ptz_service()

    # Get target profile
    media_profile = media.GetProfiles()[0]

    # Okay, so these things are some special sauce that helps fill out the camera request information.
    # Think of this as pre-filling the form that we put the x and y coordinates into later.
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    request_configuration = ptz.create_type('GetConfiguration')
    request_configuration.PTZConfigurationToken  = media_profile.PTZConfiguration.token
    ptz_configuration = ptz.GetConfiguration(request_configuration)

    request_setconfiguration = ptz.create_type('SetConfiguration')
    request_setconfiguration.PTZConfiguration = ptz_configuration

    # This is the "form" we use. See how it fills out the PanTilt.space and Zoom.space that we don't really need to 
    # fill out when we add our x and y coordinates
    global  positionrequest
    
    positionrequest = ptz.create_type('AbsoluteMove')
    positionrequest.ProfileToken = media_profile.token

    if positionrequest.Position is None :
        positionrequest.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        positionrequest.Position.PanTilt.space = ptz_configuration_options.Spaces.AbsolutePanTiltPositionSpace[0].URI
        positionrequest.Position.Zoom.space = ptz_configuration_options.Spaces.AbsoluteZoomPositionSpace[0].URI
    if positionrequest.Speed is None :
        positionrequest.Speed = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        positionrequest.Speed.PanTilt.space = ptz_configuration_options.Spaces.PanTiltSpeedSpace[0].URI

def Get_Status():
    #Get range of pan and tilt values, as well as the current position
    global XMAX, XMIN, YMAX, YMIN, XNOW, YNOW, Velocity, Zoom
    XMAX = ptz_configuration_options.Spaces.AbsolutePanTiltPositionSpace[0].XRange.Max
    XMIN = ptz_configuration_options.Spaces.AbsolutePanTiltPositionSpace[0].XRange.Min
    YMAX = ptz_configuration_options.Spaces.AbsolutePanTiltPositionSpace[0].YRange.Max
    YMIN = ptz_configuration_options.Spaces.AbsolutePanTiltPositionSpace[0].YRange.Min
    XNOW = ptz.GetStatus({'ProfileToken': media_profile.token}).Position.PanTilt.x
    YNOW = ptz.GetStatus({'ProfileToken': media_profile.token}).Position.PanTilt.y
    Velocity = ptz_configuration_options.Spaces.PanTiltSpeedSpace[0].XRange.Max
    Zoom = ptz.GetStatus({'ProfileToken': media_profile.token}).Position.Zoom.x

def do_move(ptz, request):
    global active
    #implement the request through onvif. Stops current request if interrupted
    if active:
        ptz.Stop({'ProfileToken': request.ProfileToken})
    active = True
    ptz.AbsoluteMove(request)

def abs_move(ptz, request, coord):
    # converts coordinates to request values and calls do_move to request it
    x = coord[0]; y = coord[1]
    request.Position.PanTilt.x = x
    request.Position.PanTilt.y = y
    do_move(ptz, request)

def cam_cb(data):
    #Callback function for coordinates from base station.
    global cb_request, ptz, positionrequest
    if data.x <= XMAX and data.x >= XMIN and data.y <= YMAX and data.y >= YMIN:
        cb_request = [data.x, data.y]
        abs_move(ptz, positionrequest, cb_request)

def listener():
    global active
    rospy.init_node("PTZ_Control")
    cam_sub = rospy.Subscriber('Mast', Cam, cam_cb)
    cam_fb = rospy.Publisher("Mast_Feedback", Cam, queue_size=1)
    rate = rospy.Rate(2)
    setup_move()
    currentPosition = Cam()
    while not rospy.is_shutdown():
        Get_Status()
        currentPosition.x = XNOW
        currentPosition.y = YNOW
        cam_fb.publish(currentPosition)
        rate.sleep()

if __name__ == '__main__':
    try:
        listener()
    except rospy.ROSInterruptException:
        pass
