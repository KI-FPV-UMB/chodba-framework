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
from app_utils import process_args

import time
import Adafruit_DHT

ENABLED = True
APP_NAME = "teplota_vlhkost"
APP_TYPE = "backend"
DEMO_TIME = 0
RUNON = "walle09"    #"mvagac-X230"

APP_ID, NODE_NAME, NICKNAME, APPROBATION, USER_TOPIC = process_args(sys.argv, ENABLED, APP_NAME, APP_TYPE, DEMO_TIME, RUNON)

MEASUREMENT_PAUSE = 15            # v sekundach
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

class TeplotaVlhkost(base_app.BaseApp):

    def get_app_name(self):
        return APP_NAME

    def get_app_type(self):
        return APP_TYPE

    def get_app_id(self):
        return APP_ID

    def get_node_name(self):
        return NODE_NAME

    def get_nickname(self):
        return NICKNAME

    def get_approbation(self):
        return APPROBATION

    def info_pub(self):
        return ""

    def info_sub(self):
        return ""

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
            print(json.dumps(msg))         #TODO
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
    app.start()
    app.run()


