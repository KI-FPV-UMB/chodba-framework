#!/usr/bin/python3

"""node_manager.py: spravuje konkretny uzol. tato aplikacia sa spusta priamo z os (najlepsie pri starte os), a to na kazdom uzle (1 instancia). este predtym musi byt na jednom uzle spusteny app_controller.py"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import paho.mqtt.client as mqtt
import json
import os
import logging
import subprocess
import random
import base_app


BACKEND_APPS_PATH = "../../backend-apps/"
FRONTEND_APPS_PATH = "../../frontend-apps/"

class NodeManager(base_app.BaseApp):

    def run_app(self, path, name, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None):
        p = os.path.join(path, name)
        args = []
        if os.path.isfile(os.path.join(p, name) + ".py"):
            # python app
            args.append("/usr/bin/python3")
            args.append(name + ".py")
        elif os.path.isfile(os.path.join(p, name) + ".jar"):
            # java app
            args.append("/usr/bin/java")
            args.append("-jar")
            args.append(name + ".jar")
        else:
            raise Exception("aplikacia nebola najdena alebo neznamy typ aplikacie!")
        args.append(base_app.BROKER_HOST)
        args.append(str(base_app.BROKER_PORT))

        if arg1 is None or arg2 is None:
            arg1 = "-"
            arg2 = "-"
        else:
            arg1 = str(arg1)
            arg2 = str(arg2)
        args.append(arg1)
        args.append(arg2)
        if arg3 is not None:
            args.append(arg3)
        if arg4 is not None:
            args.append(arg4)
        if arg5 is not None:
            args.append(arg5)
        subprocess.Popen(args, cwd=p)
        return None
        # ... spusti a vrat vystup
        #result = subprocess.run([f, arg1], stdout=subprocess.PIPE)
        #return result.stdout.decode("utf-8").strip("\n")

    def on_node_message(self, client, userdata, message):
        msg = json.loads(message.payload.decode())
        if not "msg" in msg:
            log = { "name": self.name, "node": self.node, "log": "neznamy typ spravy: " + str(msg) }
            self.pub_msg("log", log, "master" )
            return

        if msg["msg"] == "run":
            # spusti danu app
            try:
                if msg["type"] == "backend":
                    self.run_app(BACKEND_APPS_PATH, msg["run"])
                if msg["type"] == "frontend":
                    src = msg["src"] if "src" in msg else None
                    nick = msg["nickname"] if "nickname" in msg else None
                    approb = msg["approbation"] if "approbation" in msg else None
                    self.run_app(FRONTEND_APPS_PATH, msg["run"], self.screen_width, self.screen_height, src, nick, approb)
            except Exception as e:
                logging.exception("[" + self.name + "] chyba pri spustani " + msg["run"])
                log = { "name": self.name, "node": self.node, "log": "chyba pri spustani " + msg["run"] + ": " + str(e) }
                self.pub_msg("log", log, "master" )

        if msg["msg"] == "screen_size":
            self.screen_width = msg["width"]
            self.screen_height = msg["height"]


    def run(self):
        self.screen_width = None
        self.screen_height = None
        self.client.message_callback_add("node/" + self.node, self.on_node_message)
        self.client.subscribe("node/" + self.node)
        # spracovavaj mqtt spravy
        self.client.loop_forever()


if __name__ == '__main__':
    app = NodeManager()
    app.start()

