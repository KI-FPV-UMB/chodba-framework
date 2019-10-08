#!/usr/bin/python3

import sys
import socket
import paho.mqtt.client as mqtt
import json

BROKER_URL = "localhost"
BROKER_PORT = 1883

# zakladna trieda, ktora definuje spolocne vlastnosti pre vsetky menezovane aplikacie

class BaseApp:

    def get_app_name(self):
        # musi vratit nazov (identifikator) aplikacie
        raise NotImplementedError()

    def get_app_type(self):
        # musi vratit typ aplikacie (system/app/game)
        raise NotImplementedError()

    def info_pub(self):
        # musi vratit retazec s informaciami o topicoch, do ktorych posiela spravy
        raise NotImplementedError()

    def info_sub(self):
        # musi vratit retazec s informaciami o topicoch, na ktore sa prihlasuje
        raise NotImplementedError()

    def on_app_message(self, client, userdata, message):
        sprava = json.loads(message.payload.decode())
        if not "msg" in sprava:
            log = { 'msg': 'log', 'app': self.get_app_name(), 'log': 'neznamy typ spravy: ' + str(sprava) }
            self.client.publish(topic="master", payload=json.dumps(log), qos=0, retain=True)
            return

        if sprava["msg"] == "quit":
            self.stop()
        elif sprava["msg"] == "info":
            info = { 'msg': 'info', 'app': self.get_app_name(), 'type': self.get_app_type(), 'pub': self.info_pub(), 'sub': self.info_sub() }
            self.client.publish(topic="master", payload=json.dumps(info), qos=0, retain=True)
        elif sprava["msg"] == "status":
            status = { 'msg': 'lifecycle', 'app': self.get_app_name(), 'status': 'ok' }
            self.client.publish(topic="master", payload=json.dumps(status), qos=0, retain=True)

    def start(self):
        # priprava klienta
        self.client = mqtt.Client(self.get_app_name())

        # pripojenie k brokeru
        self.client.connect(BROKER_URL, BROKER_PORT)

        # posli spravu o startovani
        status = { 'msg': 'lifecycle', 'app': self.get_app_name(), 'type': self.get_app_type(), 'node': socket.gethostname(),'status': 'starting' }
        self.client.publish(topic="master", payload=json.dumps(status), qos=0, retain=True)

        # spracovanie systemovych sprav
        self.client.message_callback_add('apps/' + self.get_app_name(), self.on_app_message)
        self.client.subscribe("apps/" + self.get_app_name())

        # posli spravu o uspesnom nastartovani
        status = { 'msg': 'lifecycle', 'app': self.get_app_name(), 'status': 'ok' }
        self.client.publish(topic="master", payload=json.dumps(status), qos=0, retain=True)


    def stop(self):
        # posli spravu o ukoncovani
        status = { 'msg': 'lifecycle', 'app': self.get_app_name(), 'status': 'quitting' }
        self.client.publish(topic="master", payload=json.dumps(status), qos=0, retain=True)
        self.client.disconnect()


