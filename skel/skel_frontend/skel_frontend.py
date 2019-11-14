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

class SkelFrontend(base_app.BaseApp):

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_forever()

if __name__ == '__main__':
    app = SkelFrontend()
    app.process_args(sys.argv)
    app.start()

