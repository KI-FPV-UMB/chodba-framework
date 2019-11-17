#!/usr/bin/python3

"""node_manager.py: spravuje konkretny uzol. tato aplikacia sa spusta priamo z os (najlepsie pri starte os), a to na kazdom uzle (1 instancia). este predtym musi byt na jednom uzle spusteny master.py"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import paho.mqtt.client as mqtt
import json
import os
import subprocess
import random
import base_app


BACKEND_APPS_PATH = "../../backend-apps/"
FRONTEND_APPS_PATH = "../../frontend-apps/"

class NodeManager(base_app.BaseApp):

    def run_app(self, path, name, arg1=None, arg2=None, arg3=None):
        p = os.path.join(path, name)
        # test pre python app
        f = os.path.join(p, name) + ".py"
        if os.path.isfile(f):
            if arg1 is None:
                # ak je bez parametrov, spusti na pozadi
                subprocess.Popen(["/usr/bin/python3", name + ".py"], cwd=p)
                return None
            elif arg1 is not None and arg2 is None:
                # ak je 1 parameter, spusti na pozadi
                subprocess.Popen(["/usr/bin/python3", name + ".py", arg1], cwd=p)
                return None
                # ak je prave 1 parameter, spusti a vrat vystup
                #result = subprocess.run([f, arg1], stdout=subprocess.PIPE)
                #return result.stdout.decode("utf-8").strip("\n")
            elif arg1 is not None and arg2 is not None and arg3 is None:
                # ak su 2 parametre, spusti na pozadi
                subprocess.Popen(["/usr/bin/python3", name + ".py", arg1, arg2], cwd=p)
                return None
            else:
                # ak su 3 parametre, spusti na pozadi
                subprocess.Popen(["/usr/bin/python3", name + ".py", arg1, arg2, arg3], cwd=p)
                return None
        # test pre java app
        #TODO
        raise Exception("aplikacia nebola najdena alebo neznamy typ aplikacie!")

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
                    self.run_app(BACKEND_APPS_PATH, msg["name"])
                if msg["type"] == "frontend":
                    src = msg["src"] if "src" in msg else None
                    nick = msg["nickname"] if "nickname" in msg else None
                    approb = msg["approbation"] if "approbation" in msg else None
                    self.run_app(FRONTEND_APPS_PATH, msg["name"], src, nick, approb)
            except Exception as e:
                print("[" + self.name + "] chyba pri spustani " + msg["name"] + ": " + str(e))
                log = { "name": self.name, "node": self.node, "log": "chyba pri spustani " + msg["name"] + ": " + str(e) }
                self.publish_message("log", log, "master" )

    def run(self):
        self.client.message_callback_add("node/" + self.node, self.on_node_message)
        self.client.subscribe("node/" + self.node)
        # spracovavaj mqtt spravy
        self.client.loop_forever()


if __name__ == '__main__':
    app = NodeManager()
    app.start()

