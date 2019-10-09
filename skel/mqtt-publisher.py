#!/usr/bin/python3

# pip3 install paho-mqtt

import paho.mqtt.client as mqtt

# pripojenie k brokeru
broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

# publikovanie do kanala 'pokus'
client.publish(topic="pokus", payload="Hura Python!", qos=0, retain=False)

