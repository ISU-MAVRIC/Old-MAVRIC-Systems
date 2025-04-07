#!/bin/bash

#interface must be can0 or else Phoenix Tuner will not be able to flash firmware
interface=can0

if [ $# -gt 0 ]; then
    interface=$1
fi

sudo ip link set $interface type can bitrate 1000000
sudo ifconfig $interface up
sudo ifconfig $interface txqueuelen 10000
