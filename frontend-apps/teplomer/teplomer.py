#!/usr/bin/python3

"""teplomer.py: Zobrazovanie nameranej teploty (z databazy)."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import time
import matplotlib.pyplot as plt
import base_app
from app_utils import process_args

ENABLED = True
APP_NAME = "teplomer"
APP_TYPE = "frontend"
DEMO_TIME = 15

APP_ID, NODE_NAME, NICKNAME, APPROBATION, USER_TOPIC = process_args(sys.argv, ENABLED, APP_NAME, APP_TYPE, DEMO_TIME)

class Teplomer(base_app.BaseApp):

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
        # spusti spracovanie mqtt
        self.client.loop_start()
        # zobraz graf
        plt.plot([1, 2, 3, 4])
        plt.ylabel('some numbers')
        plt.show(block=False)
        # cakaj
        self.running = True
        while self.running:
            #plt.pause(1)
            time.sleep(1)
        # skonci
        plt.close()

    def stop(self):
        # zastav spracovanie mqtt
        super().stop()
        # zrus graf
        self.running = False

if __name__ == '__main__':
    app = Teplomer()
    app.start()
    app.run()


