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

import Adafruit_DHT

APP_NAME = "frontend_planner"
APP_TYPE = "backend"
DEMO_TIME = 0
RUNON = "mvagac-X230"

APP_ID, NODE_NAME, NICKNAME, APPROBATION, USER_TOPIC = process_args(sys.argv, APP_NAME, APP_TYPE, DEMO_TIME, RUNON)

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

class FrontendPlanner(base_app.BaseApp):

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

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_start()
        # meraj teplotu a vlhkost
        self.running = True
        while self.running:
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            #TODO zapis do db

    def stop(self):
        # zastav spracovanie mqtt
        super().stop()
        # zastav loop s meranim
        self.running = False


if __name__ == '__main__':
    app = FrontendPlanner()
    app.start()
    app.run()


