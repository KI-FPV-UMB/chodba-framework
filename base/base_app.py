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

    def get_status_msg(self, status):
        return { 'msg': 'lifecycle', 'name': self.get_app_name(), 'type': self.get_app_type(), 'id': self.get_app_id(), 'node': socket.gethostname(),'status': status }

    def send_message(self):
        print("TODO")       #TODO

    def on_app_message(self, client, userdata, message):
        sprava = json.loads(message.payload.decode())
        if not "msg" in sprava:
            log = { 'msg': 'log', 'name': self.get_app_name(), 'log': 'neznamy typ spravy: ' + str(sprava) }
            self.client.publish(topic="master", payload=json.dumps(log), qos=0, retain=False)
            return

        if sprava["msg"] == "quit":
            self.stop()
        elif sprava["msg"] == "info":
            info = { 'msg': 'info', 'name': self.get_app_name(), 'type': self.get_app_type(), 'id': self.get_app_id(), 'pub': self.info_pub(), 'sub': self.info_sub() }
            self.client.publish(topic="master", payload=json.dumps(info), qos=0, retain=False)
        elif sprava["msg"] == "status":
            status = self.get_status_msg('running')
            self.client.publish(topic="master", payload=json.dumps(status), qos=0, retain=False)

    def start(self):
        # priprava klienta
        self.client = mqtt.Client(self.get_node_name() + "_" + self.get_app_name() + "_" + self.get_app_id())

        # pripojenie k brokeru
        self.client.connect(BROKER_URL, BROKER_PORT)

        # spracovanie systemovych sprav
        self.client.message_callback_add('app/' + self.get_app_name(), self.on_app_message)
        self.client.subscribe("app/" + self.get_app_name())
        self.client.message_callback_add('app/' + self.get_app_name() + '/' + self.get_node_name(), self.on_app_message)
        self.client.subscribe("app/" + self.get_app_name() + '/' + self.get_node_name())

        # posli spravu o uspesnom nastartovani
        status = self.get_status_msg('running')
        self.client.publish(topic="master", payload=json.dumps(status), qos=0, retain=False)


    def stop(self):
        # posli spravu o ukoncovani
        status = self.get_status_msg('quitting')
        self.client.publish(topic="master", payload=json.dumps(status), qos=0, retain=False)
        self.client.disconnect()


