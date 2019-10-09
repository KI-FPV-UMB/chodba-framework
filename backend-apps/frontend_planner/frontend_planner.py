#!/usr/bin/python3

"""frontend_planner.py: menezuje spustanie frontend aplikacii na uzloch. ma na starosti to, aby tam vzdy nieco bezalo (t.j. ked nieco skonci, spusti nieco dalsie). tiez zabezpecuje, ze automaticky spustane appky tam budu bezat len urcity cas, potom budu nahradene inymi."""
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

APP_NAME = "frontend_planner"
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

class FrontendPlanner(base_app.BaseApp):

    def get_app_name(self):
        return APP_NAME

    def get_app_type(self):
        return APP_TYPE

    def get_app_id(self):
        return APP_ID

    def get_node_name(self):
        return NODE_NAME

    def info_pub(self):
        return ""

    def info_sub(self):
        return ""

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_forever()


if __name__ == '__main__':
    app = FrontendPlanner()
    app.start()
    app.run()


#TODO bude asi odpocuvat master topic a ked sa dozvie, ze sa daka appka skoncila, tak na danom uzle spusti nahodne dalsiu. malo by sa dako vediet, ktora appka je spustena userom a ktora takto nahodne. tie nahodne po urcitom case bude striedat. tie kde je hrac nebude moct prerusit (len po dlhsej necinnosti). na kazdom uzle musi stale bezat nejaka frontend appka. pri spustani frontend appky sa zisti, ci je daky live user. ak nie, tak by ju spustilo na viac monitorov; ak je tak len na jeden resp. ak je vedla seba volnych (neobsadenych live userom) tolko monitorov, kolko vyzaduje, tak ich spusti; inac len na 1


