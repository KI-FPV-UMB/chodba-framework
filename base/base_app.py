#!/usr/bin/python3

"""base_app.py: zakladna trieda pre frontend/backend (ale aj system) appku. implementuje to, co by mala robit kazda app"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

import sys
import socket
import paho.mqtt.client as mqtt
import json
import random
import datetime
import traceback

WEBSOCKETS = False
BROKER_URL = "localhost"
if WEBSOCKETS:
    BROKER_PORT = 9001
else:
    BROKER_PORT = 1883

# zakladna trieda, ktora definuje spolocne vlastnosti pre vsetky menezovane aplikacie

class BaseApp:

    def __init__(self):
        # inicializuj id a node
        self.id = hex(random.getrandbits(128))[2:-1]
        self.node = socket.gethostname()
        # nacitaj config a premen ho na atributy
        with open("config.json", "r") as read_file:
            config = json.load(read_file)
            for k in config.keys():
                setattr(self, k, config[k])
        # zaloguj start
        print("[" + self.name + "] spustam na uzle " + self.node)
        print("[" + self.name + "]   id = " + self.id)
        for k in config.keys():
            print("[" + self.name + "]   " + k + " = " + str(config[k]))

    def process_args(self, args):
        self.user_topic = None
        self.nickname = None
        self.approbation = None

        if len(args) > 1:
            self.user_topic = args[1]

        if len(args) > 2:
            self.nickname = args[2]

        if len(args) > 3:
            self.approbation = args[3]

    def publish_lifecycle_message(self, status):
        state = dict()
        attrs = [ "id", "name", "type", "node", "runon", "enabled", "labels", "user_topic", "nickname", "approbation" ]
        for attr in attrs:
            if getattr(self, attr, None) is not None:
                state[attr] = getattr(self, attr)
        #state = self.__dict__.copy()
        #del state["client"]
        status = { "status": status }
        msg = { **state, **status }
        self.publish_message("lifecycle", msg, "master" )

    def get_src(self):
        return "node/" + self.node + "/" + self.name

    def publish_message(self, msg_head, msg_body, topic):
        st = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        head = { "msg": msg_head, "timestamp": st, "src": self.get_src(), "name": self.name }
        if msg_body is not None:
            msg = { **head, **msg_body }
        else:
            msg = head
        self.client.publish(topic=topic, payload=json.dumps(msg), qos=0, retain=False)

    def on_msg(self, msg):
        log = { "log": "neznamy typ spravy: " + str(msg) }
        self.publish_message("log", log, "master" )

    def on_app_message(self, client, userdata, message):
        msg = json.loads(message.payload.decode())
        if not "msg" in msg:
            log = { "log": "neznamy typ spravy: " + str(msg) }
            self.publish_message("log", log, "master" )
            return

        if msg["msg"] == "quit":
            self.stop()
        elif msg["msg"] == "info":
            info = { "name": self.name, "id": self.id }
            self.publish_message("info", info, "master" )
        elif msg["msg"] == "status":
            self.publish_lifecycle_message("running")
        else:
            self.on_msg(msg)

    def start(self):
        # priprava klienta
        if WEBSOCKETS:
            self.client = mqtt.Client(self.node + "_" + self.name + "_" + self.id, transport="websockets")
        else:
            self.client = mqtt.Client(self.node + "_" + self.name + "_" + self.id)

        # pripojenie k brokeru
        self.client.connect(BROKER_URL, BROKER_PORT)

        # posli spravu o startovani (je potrebne rozlisit prve spustanie od opakujuceho sa stavu running)
        self.publish_lifecycle_message("starting")

        # spracovanie systemovych sprav
        self.client.message_callback_add("app/" + self.name, self.on_app_message)
        self.client.subscribe("app/" + self.name)
        self.client.message_callback_add("node/" + self.node + "/" + self.name, self.on_app_message)
        self.client.subscribe("node/" + self.node + "/" + self.name)

        # posli spravu o uspesnom nastartovani
        self.publish_lifecycle_message("running")

        # spusti
        try:
            self.run()
        except Exception as e:
            # zaloguj chybu
            print("[" + self.name + "] chyba pri vykonavani aplikacie: " + repr(e))
            log = { "log": "chyba pri vykonavani aplikacie: " + repr(e) }
            self.publish_message("log", log, "master" )
            traceback.print_exc()
            # skonci
            self.stop()

    def run(self):
        raise NotImplementedError()

    def stop(self):
        # posli spravu o ukoncovani
        print("[" + self.name + "] koncim na uzle " + self.node)
        self.publish_lifecycle_message("quitting")
        self.client.disconnect()


