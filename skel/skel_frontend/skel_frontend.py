#!/usr/bin/python3

"""skel_frontend.py: skel aplikacia pre frontend"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import base_app
from app_utils import process_args

APP_NAME = "skel_frontend"
APP_TYPE = "app"
DEMO_TIME = 15

APP_ID, NODE_NAME, NICKNAME, APPROBATION, RESPONSE_TOPIC = process_args(sys.argv, APP_NAME, APP_TYPE, DEMO_TIME)

class SkelFrontend(base_app.BaseApp):

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
        self.client.loop_forever()

if __name__ == '__main__':
    app = SkelFrontend()
    app.start()
    app.run()


