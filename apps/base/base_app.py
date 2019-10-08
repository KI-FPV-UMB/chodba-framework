#!/usr/bin/python3

import sys
import paho.mqtt.client as mqtt
import json

BROKER_URL = "localhost"
BROKER_PORT = 1883

# zakladna trieda, ktora definuje spolocne vlastnosti pre vsetky menezovane aplikacie

class BaseApp:

    def get_app_name(self):
        # musi vratit nazov (identifikator) aplikacie
        raise NotImplementedError()

    def info_pub(self):
        # musi vratit retazec s informaciami o topicoch, do ktorych posiela spravy
        raise NotImplementedError()

    def info_sub(self):
        # musi vratit retazec s informaciami o topicoch, na ktore sa prihlasuje
        raise NotImplementedError()

    def on_apps_message(self, client, userdata, message):
        sprava = json.loads(message.payload.decode())
        if sprava["prikaz"] == "quit":
            self.stop()
        elif sprava["prikaz"] == "info":
            info = "pub: " + self.info_pub() + "\nsub: " + self.info_sub()
            self.client.publish(topic="master", payload=info, qos=0, retain=False)
        elif sprava["prikaz"] == "status":
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


