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

NICKNAME, APPROBATION, USER_TOPIC = process_args(sys.argv)

BACKEND_APPS_PATH = "../../backend-apps/"
FRONTEND_APPS_PATH = "../../frontend-apps/"

class NodeManager(base_app.BaseApp):

    def on_node_message(self, client, userdata, message):
        msg = json.loads(message.payload.decode())
        if not "msg" in msg:
            log = { "name": self.name, "node": self.node, "log": "neznamy typ spravy: " + str(msg) }
            self.publish_message("log", log, "master" )
            return

        if msg["msg"] == "run":
            # spusti danu app
            try:
                if msg["type"] == "backend":
                    run_app(BACKEND_APPS_PATH, msg["run"])
                if msg["type"] == "frontend":
                    src = msg["src"] if "src" in msg else None
                    nick = msg["nickname"] if "nickname" in msg else None
                    approb = msg["approbation"] if "approbation" in msg else None
                    run_app(FRONTEND_APPS_PATH, msg["run"], nick, approb, src)
            except Exception as e:
                print("[" + self.name + "] chyba pri spustani " + msg["run"] + ": " + str(e))
                log = { "name": self.name, "node": self.node, "log": "chyba pri spustani " + msg["run"] + ": " + str(e) }
                self.publish_message("log", log, "master" )

    def run(self):
        self.client.message_callback_add("node/" + self.node, self.on_node_message)
        self.client.subscribe("node/" + self.node)
        # spracovavaj mqtt spravy
        self.client.loop_forever()


if __name__ == '__main__':
    app = NodeManager()
    app.start()

