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

APP_ID, NODE_NAME, NICKNAME, APPROBATION, USER_TOPIC = process_args(sys.argv, APP_NAME, APP_TYPE, "*")

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

    def get_nickname(self):
        return NICKNAME

    def get_approbation(self):
        return APPROBATION

    def info_pub(self):
        return ""

    def info_sub(self):
        return "node/" + NODE_NAME

    def on_node_message(self, client, userdata, message):
        msg = json.loads(message.payload.decode())
        if not "msg" in msg:
            log = { "name": APP_NAME, "node": NODE_NAME, "log": "neznamy typ spravy: " + str(msg) }
            self.publish_message("log", log, "master" )
            return

        if msg["msg"] == "run":
            # spusti danu app
            try:
                if msg["type"] == "backend":
                    run_app(BACKEND_APPS_PATH, msg["name"])
                if msg["type"] == "frontend":
                    src = msg["src"] if "src" in msg else None
                    nick = msg["nickname"] if "nickname" in msg else None
                    approb = msg["approbation"] if "approbation" in msg else None
                    run_app(FRONTEND_APPS_PATH, msg["name"], nick, approb, src)
            except Exception as e:
                print("[" + APP_NAME + "] chyba pri spustani " + msg["name"] + ": " + str(e))
                log = { "name": APP_NAME, "node": NODE_NAME, "log": "chyba pri spustani " + msg["name"] + ": " + str(e) }
                self.publish_message("log", log, "master" )

    def run(self):
        self.client.message_callback_add("node/" + NODE_NAME, self.on_node_message)
        self.client.subscribe("node/" + NODE_NAME)
        # spracovavaj mqtt spravy
        self.client.loop_forever()


if __name__ == '__main__':
    app = NodeManager()
    app.start()
    app.run()


