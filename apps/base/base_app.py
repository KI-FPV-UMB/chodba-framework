#!/usr/bin/python3

import sys
import paho.mqtt.client as mqtt

BROKER_URL = "localhost"
BROKER_PORT = 1883

class BaseApp:

    def get_app_name(self):
        raise NotImplementedError()

    def info(self):
        raise NotImplementedError()

    def on_apps_message(self, client, userdata, message):
        sprava = message.payload.decode()
        if sprava == "quit":
            self.stop()
        elif sprava == "info":
            self.client.publish(topic="master", payload=self.info(), qos=0, retain=False)
        elif sprava == "status":
            self.client.publish(topic="master", payload="ok", qos=0, retain=False)
        else:
            print("neznama sprava: " + sprava)

    def start(self):
        # priprava klienta
        self.client = mqtt.Client(self.get_app_name())

        # pripojenie k brokeru
        self.client.connect(BROKER_URL, BROKER_PORT)

        # spracovanie systemovych sprav
        self.client.message_callback_add('apps/' + self.get_app_name(), self.on_apps_message)
        self.client.subscribe("apps/" + self.get_app_name())

    def stop(self):
        print("koncim...")
        # posli spravu o ukoncovani
        self.client.publish(topic="master", payload="quitting", qos=0, retain=False)     #TODO sprava dako nedojde...
        self.client.disconnect()
        sys.exit(0)


