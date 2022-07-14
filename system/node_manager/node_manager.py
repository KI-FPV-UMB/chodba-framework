#!/usr/bin/python3

"""node_manager.py: This application is run directly from OS (using systemd), one instance on each node (computer). Should be started after AppController."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)

import sys
import os
import logging
import subprocess
from base import base_app
from base import app_utils

APPS_PATH = "../../apps/"

class NodeManager(base_app.BaseApp):

    def run_app(self, name, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None):
        p = os.path.join(APPS_PATH, name)
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
            raise Exception("the application " + name + " not found!")
        args.append(self.args.broker_host)
        args.append(self.args.broker_port)
        args.append(self.args.broker_transport)

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
        subprocess.Popen(args, cwd=p, stdout=sys.stdout, stderr=sys.stderr)
        return None
        # ... spusti a vrat vystup
        #result = subprocess.run([f, arg1], stdout=subprocess.PIPE)
        #return result.stdout.decode("utf-8").strip("\n")

    def get_specific_topic(self, name: str, node: str) -> list:
        return ["node/" + node]

    # def on_node_message(self, client, userdata, message):
    def on_app_msg(self, msg):
        if msg["header"][app_utils.MSG_TYPE] == "start":
            # start specified application
            try:
                nick = msg["nickname"] if "nickname" in msg else None
                approb = msg["approbation"] if "approbation" in msg else None
                self.run_app(msg["body"]["name"], self.screen_width, self.screen_height, nick, approb)
            except Exception as e:
                logging.exception("[" + self.config.name + "] error starting application " + msg["body"]["name"] + ": " + str(e))
                log = { "name": self.config.name, "node": self.node, "level": "error", "log": "error starting application " + msg["body"]["name"] + ": " + str(e) }
                self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC )

        if msg["header"][app_utils.MSG_TYPE] == "screen_size":
            self.screen_width = msg["width"]
            self.screen_height = msg["height"]


    def run(self):
        self.screen_width = None
        self.screen_height = None
        # self.client.message_callback_add("node/" + self.node, self.on_node_message)
        # self.client.subscribe("node/" + self.node)
        # spracovavaj mqtt spravy
        self.client.loop_forever()


if __name__ == '__main__':
    app = NodeManager()
    app.process_args(sys.argv)
    app.start()

