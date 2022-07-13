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
import traceback
import app_utils

class LessThanFilter(logging.Filter):
    def __init__(self, exclusive_maximum, name=""):
        super(LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        # non-zero return means we log this message
        return 1 if record.levelno < self.max_level else 0

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
        h1.addFilter(LessThanFilter(logging.WARNING))
        logger.addHandler(h1)

        h2 = logging.StreamHandler(sys.stderr)
        h2.setLevel(logging.WARNING)
        h2.setFormatter(formatter)
        logger.addHandler(h2)

        # initialize app id and node name
        self.id = hex(random.getrandbits(128))[2:-1]
        self.node = socket.gethostname()

        # read config file and set each property as an attribute
        self.config = self.read_config("./")

        # start
        logging.info("[" + self.name + "] starting on node " + self.node)
        logging.info("[" + self.name + "]   id = " + self.id)
        for k in self.config.keys():
            logging.debug("[" + self.name + "]   " + k + " = " + str(self.config[k]))

    def read_config(self, path: str):
        if not os.path.isfile(os.path.join(path, "config.json")):
            logging.error("[" + self.name + "] config file was not found in directory " + path)
            return
        with open(os.path.join(path, "config.json"), "r") as read_file:
            ret = json.load(read_file)
            if not "enabled" in ret:
                ret.enabled = True
            return ret

    def process_args(self, args):
        self.args = {}
        self.args.broker_host = args[1]
        self.args.broker_port = args[2]
        self.args.broker_transport = args[3]        # tcp / websockets
        if args[4] != "-" and args[5] != "-":
            self.args.screen_width = int(args[4])
            self.args.screen_height = int(args[5])
        else:
            self.args.screen_width = None
            self.args.screen_height = None

        if len(args) > 5:
            self.args.user_topic = args[6]
        else:
            self.args.user_topic = None

        if len(args) > 6:
            self.args.nickname = args[7]
        else:
            self.args.nickname = None

        if len(args) > 7:
            self.args.approbation = args[8]
        else:
            self.args.approbation = None

    # def get_src(self):
    #     return "node/" + self.node + "/" + self.name

    def pub_msg(self, msg_type: str, msg_body: dict, topic: str) -> None:
        """Main method for publishing messages"""
        header = {
            app_utils.MSG_TYPE: msg_type,
            "timestamp": datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'),
            "id": self.id,
            "name": self.name,
            "type": self.type,
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
        msg = json.loads(message.payload.decode())
        if not "header" in msg or not app_utils.MSG_TYPE in msg.header:
            log = { "log": "unsupported message type: " + str(msg) }
            self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)
            return

        if msg.header[app_utils.MSG_TYPE] == "stop":
            self.stop()
        elif msg.header[app_utils.MSG_TYPE] == app_utils.LIFECYCLE_STATUS:
            self.pub_lifecycle("running")
        else:
            try:
                # process specific application message
                self.on_app_msg(msg)
            except Exception as e:
                # zaloguj chybu
                logging.exception("[" + self.name + "] message processing error " + msg[app_utils.MSG_TYPE])
                log = { "log": "message processing error " + msg[app_utils.MSG_TYPE] }
                self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)

    def on_app_msg(self, msg):
        """Method for processing specific application messages (can be overloaded in child classes)"""
        log = { "log": "unknown message type: " + str(msg) }
        self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)

    def get_specific_topic(self, name: str, node: str) -> str:
        return "node/" + node + "/" + name

    def start(self):
        # prepare client
        self.client = mqtt.Client(self.node + "_" + self.name + "_" + self.id, transport=self.args.broker_transport)

        # connect to the broker
        self.client.connect(self.args.broker_host, self.args.broker_port)

        # send lifecycle status 'starting' (it is necessary to distinguish starting status from repeating running status)
        self.pub_lifecycle("starting")

        # list to incoming messages
        logging.info("[" + self.name + "] binding to " + self.get_specific_topic(self.name, self.node) + " topic")
        self.client.message_callback_add(self.get_specific_topic(self.name, self.node), self.on_msg)
        self.client.subscribe(self.get_specific_topic(self.name, self.node))

        # send lifecycle status 'running'
        self.pub_lifecycle("running")

        # run
        try:
            self.run()
        except Exception as e:
            # log exception
            logging.exception("[" + self.name + "] exception running application")     # repr(e)
            log = { "log": "exception running application: " + repr(e) }
            self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)
            #traceback.print_exc()      #TODO malo by byt obsiahnute v logging.exception()
            # skonci
            self.stop()

    def run(self):
        raise NotImplementedError()

    def stop(self):
        # send lifecycle status 'stopping'
        logging.info("[" + self.name + "] stopping on node " + self.node)
        self.pub_lifecycle("stopping")
        self.client.disconnect()


