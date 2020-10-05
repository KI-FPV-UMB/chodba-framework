#!/bin/bash

# echo 'standby 0' | cec-client -s -d 1
# https://www.screenly.io/blog/2017/07/02/how-to-automatically-turn-off-and-on-your-monitor-from-your-raspberry-pi/

#ExecStartPre=xset -display :0.0 -dpms
#ExecStartPre=xset -display :0.0 s off
#ExecStartPre=xset -display :0.0 s noblank

if [ "$1" == "on" ]
then
	vcgencmd display_power 1
fi

if [ "$1" == "off" ]
then
	vcgencmd display_power 0
fi

