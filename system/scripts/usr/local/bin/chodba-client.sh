#!/bin/sh

if [ $# -lt 1 ]
then
	echo "supported arguments:"
	echo "  stat"
	echo "  start <name> <node>"
	echo "  stop <name> <node>"
	exit
fi

ARG=$1

case $ARG in
	stat)
		mosquitto_pub -t app_controller -m '{"header":{"msg": "stat"}}'
		;;
	start)
		NAME=$2
		NODE=$3
		#MSG="{'header': {'msg': 'start'},'body': {'type': '$TYPE', 'name': '$NAME'}}"
		MSG='{"header": {"msg": "start"},"body": {"name": "'$NAME'"}}'
		mosquitto_pub -t node/$NODE -m "$MSG"
		;;
	stop)
		NAME=$2
		NODE=$3
		MSG='{"header": {"msg": "stop"}}'
		echo "stopping node/$NODE/$NAME"
		mosquitto_pub -t "node/$NODE/$NAME" -m "$MSG"
		;;
	*)
		echo "unsupported argument $ARG"
esac


#mosquitto_sub -d -t app_controller
#mosquitto_pub -t app_controller -m '{"msg": "start_backends"}'
#mosquitto_pub -t app_controller -m '{"msg": "applications", "response_topic": "qwe"}'
#mosquitto_pub -t app_controller -m '{"msg": "applications", "response_topic": "qwe", "filter": "running"}'
#mosquitto_pub -t app_controller -m '{"msg": "applications", "response_topic": "qwe", "filter": "running", "type":"system"}'
#mosquitto_pub -t app_controller -m '{"msg": "applications", "type": "app", "response_topic": "qwe"}'
#mosquitto_pub -t app_controller -m '{"msg": "workspaces", "response_topic": "qwe"}'
#mosquitto_pub -t app_controller -m '{"msg": "approbations", "response_topic": "qwe"}'
#mosquitto_pub -t app/app_controller -m '{"msg": "info"}'
#mosquitto_pub -t app/app_controller -m '{"msg": "quit"}'
#mosquitto_pub -t app/app_controller/mvagac-X230 -m '{"msg": "quit"}'
#mosquitto_pub -t node/mvagac-X230 -m '{"msg": "run", "type": "frontend", "name": "demo_hra2d_p"}'


