#!/usr/bin/python3

"""skel_backend.py: skel aplikacia pre backend v pythone"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import base_app

class SkelBackend(base_app.BaseApp):

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_forever()


if __name__ == '__main__':
    app = SkelBackend()
    app.process_args(sys.argv)
    app.start()

