#!/usr/bin/python3

# pip3 install paho-mqtt

import paho.mqtt.client as mqtt

# pripojenie k brokeru
broker_url = "localhost"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

# odoberanie z kanala 'pokus'
def on_message(client, userdata, message):
       print("prijata sprava: " + message.topic + ", " + message.payload.decode())
client.on_message = on_message
client.subscribe("pokus")
client.loop_forever()

