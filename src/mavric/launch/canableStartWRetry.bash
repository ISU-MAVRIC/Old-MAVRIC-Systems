#!/bin/bash

for((iterator=0;iterator<10;iterator++))
do
  /home/mavric/catkin_ws/src/mavric/launch/canableStart.bash

  N_CANIFACE=$(ifconfig | grep -c "^can")
  if [ $N_CANIFACE -gt 0 ]
  then
    break
  fi
done
