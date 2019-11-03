#!/usr/bin/python3

"""base_app.py: zakladna trieda pre frontend/backend (ale aj system) appku. implementuje to, co by mala robit kazda app"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

import sys
import socket
import paho.mqtt.client as mqtt
import json

BROKER_URL = "localhost"
BROKER_PORT = 1883

# zakladna trieda, ktora definuje spolocne vlastnosti pre vsetky menezovane aplikacie

class BaseApp:

    def get_app_name(self):
        # musi vratit nazov aplikacie
        raise NotImplementedError()

    def get_app_type(self):
        # musi vratit typ aplikacie (system/app/game)
        raise NotImplementedError()

    def get_app_id(self):
        # musi vratit unikatny identifikator aplikacie
        raise NotImplementedError()

    def get_node_name(self):
        # musi vratit hostname, kde je spusteny
        raise NotImplementedError()

    def info_pub(self):
        # musi vratit retazec s informaciami o topicoch, do ktorych posiela spravy
        raise NotImplementedError()

    def info_sub(self):
        # musi vratit retazec s informaciami o topicoch, na ktore sa prihlasuje
        raise NotImplementedError()

    def get_lifecycle_msg(self, status):
        return { "name": self.get_app_name(), "type": self.get_app_type(), "id": self.get_app_id(), "node": socket.gethostname(),"status": status }

    def publish_message(self, msg_head, msg_body, topic):
        head = { "msg": msg_head, "src": "node/" + self.get_node_name() + "/" + self.get_app_name() }
        #TODO podla moznosti pribalit nickname, approb, ...
        msg = { **head, **msg_body }
        self.client.publish(topic=topic, payload=json.dumps(msg), qos=0, retain=False)

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
            status = self.get_lifecycle_msg("running")
            self.publish_message("lifecycle", status, "master" )
        else:
            log = { "log": "neznamy typ spravy: " + str(msg) }
            self.publish_message("log", log, "master" )

    def start(self):
        # priprava klienta
        self.client = mqtt.Client(self.get_node_name() + "_" + self.get_app_name() + "_" + self.get_app_id())

        # pripojenie k brokeru
        self.client.connect(BROKER_URL, BROKER_PORT)

        # spracovanie systemovych sprav
        self.client.message_callback_add("app/" + self.get_app_name(), self.on_app_message)
        self.client.subscribe("app/" + self.get_app_name())
        self.client.message_callback_add("node/" + self.get_node_name() + "/" + self.get_app_name(), self.on_app_message)
        self.client.subscribe("node/" + self.get_node_name() + "/" + self.get_app_name())

        # posli spravu o uspesnom nastartovani
        status = self.get_lifecycle_msg("running")
        self.publish_message("lifecycle", status, "master" )


    def stop(self):
        # posli spravu o ukoncovani
        print("[" + self.get_app_name() + "] koncim na uzle " + self.get_node_name())
        status = self.get_lifecycle_msg("quitting")
        self.publish_message("lifecycle", status, "master" )
        self.client.disconnect()


