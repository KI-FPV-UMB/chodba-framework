#!/usr/bin/python3

"""teplota_vlhkost.py: v pravidelnom intervale zmeria teplotu a vlhkost a zapise ju do databazy."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import base_app
import time
import Adafruit_DHT

MEASUREMENT_PAUSE = 15            # v sekundach
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

class TeplotaVlhkost(base_app.BaseApp):

    def on_msg(self, msg):
        None

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_start()
        # meraj teplotu a vlhkost
        self.running = True
        while self.running:
            # zmeraj vlhkost a teplotu
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            # zapis do db
            msg = { "humidity": humidity, "temperature": temperature }
            self.publish_message("insert", msg, "database")
            # cakaj
            time.sleep(MEASUREMENT_PAUSE)

    def stop(self):
        # zastav spracovanie mqtt
        super().stop()
        # zastav loop s meranim
        self.running = False


if __name__ == '__main__':
    app = TeplotaVlhkost()
    app.process_args(sys.argv)
    app.start()

