#!/bin/bash

# spustat cronom kazde 2 minuty

# oprav bridge
BR_CHECK=$(brctl show | grep wlan0)
if [ "$BR_CHECK" == "" ]
then
	echo "opravujem..."
	brctl addif br0 wlan0
fi

# nahode node_manager (ak treba)
#NM_CHECK=$(ps -ef |grep "node_manager.py" | grep -v grep)
#if [ "$NM_CHECK" == "" ]
#then
#	/home/pi/chodba-framework-app_controller/system/node_manager/node_manager.sh
#fi

