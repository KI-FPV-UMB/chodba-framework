#!/bin/sh

# start on main node (with AppController)

HOSTNAME=$(hostname)
NODES=$(cat /etc/hosts | grep chodba | grep -v $HOSTNAME | sort | awk '{ print $2 }')

# stop all nodes
for NODE in $NODES
do
  ssh $NODE 'sudo systemctl stop chodba-node_manager.service'
done


# start all nodes
for NODE in $NODES
do
  ssh $NODE 'sudo systemctl start chodba-node_manager.service'
done
