#!/bin/sh

export DISPLAY=:0.0
xset s off
xset -display :0.0 -dpms
xset -display :0.0 s off
xset -display :0.0 s noblank

export PYTHONPATH=/home/pi/chodba-framework-master/base

#cd /home/pi/chodba-framework-master/system/node_manager
#./node_manager.py > /tmp/chodba-node_manager.log 2>&1 &
./node_manager.py

