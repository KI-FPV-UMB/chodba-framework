#!/bin/sh

ip a > /tmp/chodba-ki01-ip.txt
scp /tmp/chodba-ki01-ip.txt remotestat@io.fpv.umb.sk:
rm /tmp/chodba-ki01-ip.txt

