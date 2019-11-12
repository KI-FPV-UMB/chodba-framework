#!/usr/bin/python3

"""base_app.py: zakladna trieda pre frontend/backend (ale aj system) appku. implementuje to, co by mala robit kazda app"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

import sys
import socket
import paho.mqtt.client as mqtt
import json
import time
import datetime

WEBSOCKETS = False
BROKER_URL = "localhost"
if WEBSOCKETS:
    BROKER_PORT = 9001
else:
    BROKER_PORT = 1883

# zakladna trieda, ktora definuje spolocne vlastnosti pre vsetky menezovane aplikacie

class BaseApp:

    def get_app_name(self):
        # musi vratit nazov aplikacie
        raise NotImplementedError()

    def get_app_type(self):
        # musi vratit typ aplikacie (system/backend/frontend)
        raise NotImplementedError()

    def get_app_id(self):
        # musi vratit unikatny identifikator aplikacie
        raise NotImplementedError()

    def get_node_name(self):
        # musi vratit hostname, kde je spusteny
        raise NotImplementedError()

    def get_demo_time(self):
        # musi vratit cas, kolko bude bezat ako demo
        return 0

    def get_nickname(self):
        # musi vratit nickname, pod ktorym bol spusteny
        raise NotImplementedError()

    def get_approbation(self):
        # musi vratit aprobaciu, pod ktorou bol spusteny
        raise NotImplementedError()

    def info_pub(self):
        # musi vratit retazec s informaciami o topicoch, do ktorych posiela spravy
        raise NotImplementedError()

    def info_sub(self):
        # musi vratit retazec s informaciami o topicoch, na ktore sa prihlasuje
        raise NotImplementedError()

    def publish_lifecycle_message(self, status):
        status = { "name": self.get_app_name(), "type": self.get_app_type(), "id": self.get_app_id(), "node": self.get_node_name(), "demo_time": self.get_demo_time(), "status": status }
        if self.get_nickname() is not None:
            status["nickname"] = self.get_nickname()
        if self.get_approbation() is not None:
            status["approbation"] = self.get_approbation()
        self.publish_message("lifecycle", status, "master" )

    def publish_message(self, msg_head, msg_body, topic):
        ts = time.time()
        #st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S%f')
        head = { "msg": msg_head, "timestamp": st, "src": "node/" + self.get_node_name() + "/" + self.get_app_name(), "app_name": self.get_app_name() }
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
            info = { "name": self.get_app_name(), "type": self.get_app_type(), "id": self.get_app_id(), "pub": self.info_pub(), "sub": self.info_sub() }
            self.publish_message("info", info, "master" )
        elif msg["msg"] == "status":
            self.publish_lifecycle_message("running")
        else:
            self.on_msg(msg)

    def start(self):
        # priprava klienta
        if WEBSOCKETS:
            self.client = mqtt.Client(self.get_node_name() + "_" + self.get_app_name() + "_" + self.get_app_id(), transport="websockets")
        else:
            self.client = mqtt.Client(self.get_node_name() + "_" + self.get_app_name() + "_" + self.get_app_id())

        # pripojenie k brokeru
        self.client.connect(BROKER_URL, BROKER_PORT)

        # posli spravu o startovani (je potrebne rozlisit prve spustanie od opakujuceho sa stavu running)
        self.publish_lifecycle_message("starting")

        # spracovanie systemovych sprav
        self.client.message_callback_add("app/" + self.get_app_name(), self.on_app_message)
        self.client.subscribe("app/" + self.get_app_name())
        self.client.message_callback_add("node/" + self.get_node_name() + "/" + self.get_app_name(), self.on_app_message)
        self.client.subscribe("node/" + self.get_node_name() + "/" + self.get_app_name())

        # posli spravu o uspesnom nastartovani
        self.publish_lifecycle_message("running")


    def stop(self):
        # posli spravu o ukoncovani
        print("[" + self.get_app_name() + "] koncim na uzle " + self.get_node_name())
        self.publish_lifecycle_message("quitting")
        self.client.disconnect()


