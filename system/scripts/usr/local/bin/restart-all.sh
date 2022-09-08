#!/bin/sh

# start on main node (with AppController)

HOSTNAME=$(hostname)
NODES=$(cat /etc/hosts | grep chodba | grep -v $HOSTNAME | sort | awk '{ print $2 }')

# stop all nodes and clear logs
for NODE in $NODES
do
  echo "stopping $NODE"
  ssh $NODE 'sudo systemctl daemon-reload'
  ssh $NODE 'sudo systemctl stop chodba-node_manager.service'
  ssh $NODE 'sudo rm /var/log/chodba/*'
done

# handle current (main) node
echo "stopping $HOSTNAME"
sudo systemctl stop chodba-node_manager.service
sudo systemctl stop chodba-app_controller.service

sudo rm /var/log/chodba/*

echo "starting $HOSTNAME"
sudo systemctl start chodba-app_controller.service
sudo systemctl start chodba-node_manager.service

# start all nodes
for NODE in $NODES
do
  echo "starting $NODE"
  ssh $NODE 'sudo systemctl start chodba-node_manager.service'
done
