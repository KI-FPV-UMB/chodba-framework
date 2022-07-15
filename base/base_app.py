#!/usr/bin/python3

"""base_app.py: basic class for frontend/backend/system application. Implements minimal required functionality for each application."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

import sys
import socket
import os
import paho.mqtt.client as mqtt
import json
import random
import datetime
import logging
import threading
import traceback
from base import app_utils

class LessThanFilter(logging.Filter):
    def __init__(self, exclusive_maximum, name=""):
        super(LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        # non-zero return means we log this message
        return 1 if record.levelno < self.max_level else 0

class Config:
    def __init__(self):
        self.name = None

class Args:
    pass

class BaseApp:
    """Basic class defining common properties for all applications"""

    def __init__(self):
        #logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)

        formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")

        h1 = logging.StreamHandler(sys.stdout)
        h1.setLevel(logging.DEBUG)
        h1.setFormatter(formatter)
        # h1.addFilter(LessThanFilter(logging.WARNING))
        logger.addHandler(h1)

        h2 = logging.StreamHandler(sys.stderr)
        h2.setLevel(logging.WARNING)
        h2.setFormatter(formatter)
        logger.addHandler(h2)

        # initialize app id and node name
        self.id = hex(random.getrandbits(128))[2:-1]
        self.node = socket.gethostname()

        # read config file and set each property as an attribute
        self.config = Config()
        conf = self.read_config("./")
        for k in conf.keys():
            setattr(self.config, k, conf[k])

        self.debug = False

        # start
        logging.info("[" + self.config.name + "] starting on node " + self.node)
        logging.info("[" + self.config.name + "]   id = " + self.id)
        for k in conf.keys():
            logging.debug("[" + self.config.name + "]   " + k + " = " + str(conf[k]))

    def read_config(self, path: str):
        cf = os.path.join(path, "config.json")
        if not os.path.isfile(cf):
            logging.error("[" + self.config.name + "] config file was not found in directory " + path)
            return

        try:
            with open(cf, "r") as read_file:
                ret = json.load(read_file)
                if not "enabled" in ret:
                    ret["enabled"] = True
                return ret
        except Exception as e:
            # log exception
            logging.exception("[" + self.config.name + "] error reading file " + cf)     # repr(e)
            return

    def process_args(self, args):
        self.args = Args()
        if len(args) < 3:
            logging.error("[" + self.config.name + "] You must provide at least following 3 mandatory arguments: broker_host broker_port broker_transport")
            sys.exit(1)
        self.args.broker_host = args[1]
        self.args.broker_port = args[2]
        self.args.broker_transport = args[3]        # tcp / websockets

        if len(args) < 5 or args[4] == "-" or args[5] == "-":
            self.args.screen_width = None
            self.args.screen_height = None
        else:
            self.args.screen_width = int(args[4])
            self.args.screen_height = int(args[5])

        if len(args) > 6:
            self.args.user_topic = args[6]
        else:
            self.args.user_topic = None

        if len(args) > 7:
            self.args.nickname = args[7]
        else:
            self.args.nickname = None

        if len(args) > 8:
            self.args.approbation = args[8]
        else:
            self.args.approbation = None

    # def get_src(self):
    #     return "node/" + self.node + "/" + self.config.name

    def pub_msg(self, msg_type: str, msg_body: dict, topic: str) -> None:
        """Main method for publishing messages"""
        header = {
            app_utils.MSG_TYPE: msg_type,
            "timestamp": datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'),
            "id": self.id,
            "name": self.config.name,
            "type": self.config.type,
            "node": self.node
        }
        msg = {"header": header}
        if msg_body is not None:
            msg["body"] = msg_body
        self.client.publish(topic=topic, payload=json.dumps(msg), qos=0, retain=False)

    def pub_lifecycle(self, status: str) -> None:
        """Publish lifecycle message, such as starting/running/stopping/etc."""
        self.pub_msg(app_utils.MSG_TYPE_LIFECYCLE, { app_utils.LIFECYCLE_STATUS: status }, app_utils.APP_CONTROLLER_TOPIC)

    def on_msg(self, client, userdata, message):
        """basic method for retrieving messages"""
        try:
            msg = json.loads(message.payload.decode())
        except Exception as e:
            logging.exception("[" + self.config.name + "] message format error: " + repr(e))
            log = {"name": self.config.name, "node": self.node, "level": "error",
                   "log": "message format error: " + repr(e)}
            self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)
            return

        if not "header" in msg or not app_utils.MSG_TYPE in msg["header"]:
            logging.warning("[" + self.config.name + "] unsupported message type: " + str(msg))
            log = { "name": self.config.name, "node": self.node, "level": "warning", "log": "unsupported message type: " + str(msg) }
            self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)
            return

        msg_type = msg["header"][app_utils.MSG_TYPE]
        if msg_type == "stop":
            self.stop()
        elif msg_type == app_utils.LIFECYCLE_STATUS:
            self.pub_lifecycle("running")
        elif msg_type == "debug":
            if msg["body"]["state"] == "on" or msg["body"]["state"] == "true":
                self.debug = True
            else:
                self.debug = False
            logging.info("[" + self.config.name + "] changing debugging state to " + self.debug)
        else:
            try:
                # process specific application message
                self.on_app_msg(msg)
            except Exception as e:
                logging.exception("[" + self.config.name + "] error processing message '" + msg_type + "': " + repr(e))
                log = { "name": self.config.name, "node": self.node, "level": "error", "log": "error processing message '" + msg_type + "': " + repr(e)}
                self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)

    def on_app_msg(self, msg):
        """Method for processing specific application messages (can be overloaded in child classes)"""
        logging.warning("[" + self.config.name + "] unsupported message type: " + str(msg))
        log = { "name": self.config.name, "node": self.node, "level": "warning", "log": "unknown message type: " + str(msg) }
        self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)

    def get_specific_topic(self, name: str, node: str) -> list:
        return ["node/" + node + "/" + name]

    def start(self):
        # prepare client
        self.client = mqtt.Client(self.node + "_" + self.config.name + "_" + self.id, transport=self.args.broker_transport)

        # connect to the broker
        self.client.connect(self.args.broker_host, int(self.args.broker_port))

        # send lifecycle status 'starting' (it is necessary to distinguish starting status from repeating running status)
        self.pub_lifecycle("starting")

        # list to incoming messages
        for t in self.get_specific_topic(self.config.name, self.node):
            logging.info("[" + self.config.name + "] binding to topic: " + t)
            self.client.message_callback_add(t, self.on_msg)
            self.client.subscribe(t)

        # run
        try:
            self.run()
        except Exception as e:
            # log exception
            logging.exception("[" + self.config.name + "] exception running application: " + repr(e))
            log = { "name": self.config.name, "node": self.node, "level": "error", "log": "exception running application: " + repr(e) }
            self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)
            #traceback.print_exc()      #TODO malo by byt obsiahnute v logging.exception()
            # skonci
            self.stop()

    def run(self):
        # send lifecycle status 'running' (only after this message will count demo_time)
        logging.info("[" + self.config.name + "] running")
        self.pub_lifecycle("running")

        if hasattr(self.config, 'demo_time'):
            # since it is demo, schedule stopping of the application (only now, after it is already running)
            t = threading.Timer(int(self.config.demo_time), self.stop, [])
            t.start()

    def stop(self):
        # send lifecycle status 'stopping'
        logging.info("[" + self.config.name + "] stopping on node " + self.node)
        self.pub_lifecycle("stopping")
        self.client.disconnect()


