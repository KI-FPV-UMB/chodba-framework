#!/usr/bin/python3

"""node_manager.py: This application is run directly from OS (using systemd), one instance on each node (computer). Should be started after AppController."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)

import sys
import os
import logging
import threading
import subprocess
from base import base_app
from base import app_utils

APPS_PATH = "../../apps/"

class AppRunner(threading.Thread):
    def __init__(self, name, broker_host, broker_port, broker_transport, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None):
        super().__init__()
        self.app_name = name
        # process arguments
        p = os.path.join(APPS_PATH, self.app_name)
        self.pargs = []
        if os.path.isfile(os.path.join(p, self.app_name) + ".py"):
            # python app
            self.pargs.append("/usr/bin/python3")
            self.pargs.append(self.app_name + ".py")
        elif os.path.isfile(os.path.join(p, self.app_name) + ".jar"):
            # java app
            self.pargs.append("/usr/bin/java")
            self.pargs.append("-jar")
            self.pargs.append(self.app_name + ".jar")
        else:
            raise Exception("the application " + self.app_name + " not found!")
        self.pargs.append(broker_host)
        self.pargs.append(broker_port)
        self.pargs.append(broker_transport)

        if arg1 is None or arg2 is None:
            arg1 = "-"
            arg2 = "-"
        else:
            arg1 = str(arg1)
            arg2 = str(arg2)
        self.pargs.append(arg1)
        self.pargs.append(arg2)
        if arg3 is not None:
            self.pargs.append(arg3)
        if arg4 is not None:
            self.pargs.append(arg4)
        if arg5 is not None:
            self.pargs.append(arg5)

        # start in thread (to wait to result to avoid a zombie process)
        threading.Thread.__init__(self)

    def run(self):
        p = os.path.join(APPS_PATH, self.app_name)
        p = subprocess.Popen(self.pargs, cwd=p, stdout=sys.stdout, stderr=sys.stderr)
        p.wait()

class NodeManager(base_app.BaseApp):

    def run_app(self, name, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None):
        return None
        # ... spusti a vrat vystup
        #result = subprocess.run([f, arg1], stdout=subprocess.PIPE)
        #return result.stdout.decode("utf-8").strip("\n")

    def get_specific_topic(self, name: str, node: str) -> list:
        return ["node/" + node]

    def on_app_msg(self, msg):
        """basic method for retrieving messages"""
        msg_type = msg["header"][app_utils.MSG_TYPE]

        if msg_type == "start":
            # start specified application
            name = msg["body"]["name"]
            try:
                app_config = self.read_config(os.path.join(APPS_PATH, name))
                if app_config is not None:
                    if app_config["enabled"]:
                        nick = msg["nickname"] if "nickname" in msg else None
                        approb = msg["approbation"] if "approbation" in msg else None
                        app_runner = AppRunner(name, self.args.broker_host, self.args.broker_port, self.args.broker_transport,
                                               self.screen_width, self.screen_height, nick, approb)
                        app_runner.start()
                    else:
                        logging.warning("[" + self.config.name + "] application " + name + " is disabled")
                        log = {"name": self.config.name, "node": self.node, "level": "warning", "log": "application " + name + " is disabled"}
                        self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)
            except Exception as e:
                logging.exception("[" + self.config.name + "] error starting application " + name + ": " + str(e))
                log = { "name": self.config.name, "node": self.node, "level": "error", "log": "error starting application " + name + ": " + str(e) }
                self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC )

        elif msg_type == "screen_size":
            self.screen_width = msg["width"]
            self.screen_height = msg["height"]

        else:
            super().on_app_msg(msg)


    def run(self):
        super().run()

        self.screen_width = None
        self.screen_height = None

        # start processing of mqtt messages
        self.client.loop_forever()


if __name__ == '__main__':
    app = NodeManager()
    app.process_args(sys.argv)
    app.start()

