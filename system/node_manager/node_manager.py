#!/usr/bin/python3

"""node_manager.py: spravuje konkretny uzol. tato aplikacia sa spusta priamo z os (najlepsie pri starte os), a to na kazdom uzle (1 instancia). este predtym musi byt na jednom uzle spusteny master.py"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import paho.mqtt.client as mqtt
import json
import base_app
from app_utils import process_args
from app_utils import run_app

APP_NAME = "node_manager"
APP_TYPE = "system"

APP_ID, NODE_NAME, NICKNAME, APPROBATION, RESPONSE_TOPIC = process_args(sys.argv, APP_NAME, APP_TYPE, "*")

BACKEND_APPS_PATH = "../../backend-apps/"
FRONTEND_APPS_PATH = "../../frontend-apps/"

class NodeManager(base_app.BaseApp):

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
                    run_app(FRONTEND_APPS_PATH, sprava["name"], sprava["nickname"], sprava["approbation"], sprava["response_topic"])
            except Exception as e:
                print("[" + APP_NAME + "] chyba pri spustani " + sprava["name"] + ": " + str(e))
                log = { 'msg': 'log', 'name': APP_NAME, 'node': NODE_NAME, 'log': 'chyba pri spustani ' + sprava["name"] + ": " + str(e) }
                self.client.publish(topic="master", payload=json.dumps(log), qos=0, retain=False)

    def run(self):
        self.client.message_callback_add('node/' + NODE_NAME, self.on_node_message)
        self.client.subscribe("node/" + NODE_NAME)
        # spracovavaj mqtt spravy
        self.client.loop_forever()


if __name__ == '__main__':
    app = NodeManager()
    app.start()
    app.run()


