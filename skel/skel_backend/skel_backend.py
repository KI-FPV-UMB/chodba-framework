#!/usr/bin/python3

"""skel_backend.py: skel aplikacia pre backend v pythone"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import random
import socket
import paho.mqtt.client as mqtt
import json
import base_app

APP_NAME = "skel_backend"
APP_TYPE = "app"
APP_ID = hex(random.getrandbits(128))[2:-1]

# na poziadnie oznam typ
if len(sys.argv) == 2 and sys.argv[1]=="type":
    print(APP_TYPE)
    sys.exit(1)

# na poziadnie oznam, kde sa ma spustit: * na vsetkych, ? na lubovolnom, <nazov> na konkretnom
if len(sys.argv) == 2 and sys.argv[1]=="runon":
    print("mvagac-X230")        # nazov master uzla
    sys.exit(1)

# nazov uzla je dany hostname
NODE_NAME = socket.gethostname()
print("[" + APP_NAME + "] spustam na uzle " + NODE_NAME)

class SkelBackend(base_app.BaseApp):

    def get_app_name(self):
        return APP_NAME

    def get_app_type(self):
        return APP_TYPE

    def get_app_id(self):
        return APP_ID

    def info_pub(self):
        return ""

    def info_sub(self):
        return ""

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_forever()


if __name__ == '__main__':
    app = SkelBackend()
    app.start()
    app.run()



