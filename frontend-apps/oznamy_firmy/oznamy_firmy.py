#!/usr/bin/python3

# PYTHONPATH musi odkazoat na absolutnu cestu k .../chodba-framework/base

# tato aplikacia sa spusta priamo z os (vzdy pri starte os); a to len na hlavnom uzle. musi sa spustit ako prva

import sys
import os
import random
import socket
import paho.mqtt.client as mqtt
import json
import base_app

APP_NAME = "oznamy_firmy"
APP_TYPE = "app"
APP_ID = hex(random.getrandbits(128))[2:-1]

# na poziadnie oznam typ
if len(sys.argv) == 2 and sys.argv[1]=="type":
    print(APP_TYPE)
    sys.exit(1)

# nazov uzla je dany hostname
NODE_NAME = socket.gethostname()
print("[" + APP_NAME + "] nazov uzla: " + NODE_NAME)

class OznamyFirmy(base_app.BaseApp):

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
        # cakaj
        self.client.loop_forever()


if __name__ == '__main__':
    app = OznamyFirmy()
    app.start()
    app.run()


#TODO 


