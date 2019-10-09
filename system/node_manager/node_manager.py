#!/usr/bin/python3

# PYTHONPATH musi odkazoat na absolutnu cestu k .../chodba-framework/base

# tato aplikacia sa spusta priamo z os (vzdy pri starte os); a to na kazdom uzle

import sys
import random
import socket
import paho.mqtt.client as mqtt
import json
import base_app
from app_utils import run_app

APP_NAME = "node_manager"
APP_TYPE = "system"
APP_ID = hex(random.getrandbits(128))[2:-1]

BACKEND_APPS_PATH = "../../backend-apps/"
FRONTEND_APPS_PATH = "../../frontend-apps/"

# na poziadnie oznam typ
if len(sys.argv) == 2 and sys.argv[1]=="type":
    print(APP_TYPE)
    sys.exit(1)

# na poziadnie oznam, kde sa ma spustit: * na vsetkych, ? na lubovolnom, <nazov> na konkretnom
if len(sys.argv) == 2 and sys.argv[1]=="runon":
    # zobraz informaciu, na ktorych uzloch sa ma backend spustat
    print("*")
    sys.exit(1)

# nazov uzla je dany hostname
NODE_NAME = socket.gethostname()
print("[" + APP_NAME + "] nazov uzla: " + NODE_NAME)

class NodeManager(base_app.BaseApp):

    def get_app_name(self):
        return APP_NAME

    def get_app_type(self):
        return APP_TYPE

    def get_app_id(self):
        return APP_ID

    def info_pub(self):
        return ""

    def info_sub(self):
        return "node/" + NODE_NAME

    def on_node_message(self, client, userdata, message):
        sprava = json.loads(message.payload.decode())
        if not "msg" in sprava:
            log = { 'msg': 'log', 'name': APP_NAME, 'node': NODE_NAME, 'log': 'neznamy typ spravy: ' + str(sprava) }
            self.client.publish(topic="master", payload=json.dumps(log), qos=0, retain=False)
            return

        if sprava["msg"] == "run":
            # spusti danu app
            try:
                if sprava["type"] == "backend":
                    run_app(BACKEND_APPS_PATH, sprava["name"])
                if sprava["type"] == "frontend":
                    run_app(FRONTEND_APPS_PATH, sprava["name"])
            except Exception as e:
                print("[" + APP_NAME + "] chyba pri spustani " + sprava["name"] + ": " + str(e))
                log = { 'msg': 'log', 'name': APP_NAME, 'node': NODE_NAME, 'log': 'chyba pri spustani ' + sprava["name"] + ": " + str(e) }
                self.client.publish(topic="master", payload=json.dumps(log), qos=0, retain=False)
            #TODO asi pocitat aj s argumentami. priklad: teplomer_alert a b c => spusti danu appku nasledovne: teplomer_alert NODE_NAME a b c

    def run(self):
        self.client.message_callback_add('node/' + NODE_NAME, self.on_node_message)
        self.client.subscribe("node/" + NODE_NAME)
        # cakaj
        self.client.loop_forever()


if __name__ == '__main__':
    app = NodeManager()
    app.start()
    app.run()


