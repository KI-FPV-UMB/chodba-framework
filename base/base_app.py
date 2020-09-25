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
import logging
import traceback

WEBSOCKETS = False

#with open ("/etc/hostname", "r") as f:
#    hn=f.readlines()
#if hn.trim()=="chodba-ki01":
#        BROKER_HOST = "localhost"
#    else:
#        BROKER_HOST = "localhost"

BROKER_HOST = "chodba-ki01"
if WEBSOCKETS:
    BROKER_PORT = 9001
else:
    BROKER_PORT = 1883

class LessThanFilter(logging.Filter):
    def __init__(self, exclusive_maximum, name=""):
        super(LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        # non-zero return means we log this message
        return 1 if record.levelno < self.max_level else 0

# zakladna trieda, ktora definuje spolocne vlastnosti pre vsetky menezovane aplikacie
class BaseApp:

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

        # inicializuj id a node
        self.id = hex(random.getrandbits(128))[2:-1]
        self.node = socket.gethostname()
        # nacitaj config a premen ho na atributy
        with open("config.json", "r") as read_file:
            config = json.load(read_file)
            for k in config.keys():
                setattr(self, k, config[k])
        # zaloguj start
        logging.info("[" + self.name + "] spustam na uzle " + self.node)
        logging.info("[" + self.name + "]   id = " + self.id)
        for k in config.keys():
            logging.debug("[" + self.name + "]   " + k + " = " + str(config[k]))

    def process_args(self, args):
        self.broker_host = args[1]
        self.broker_port = args[2]
        if args[3] != "-" and args[4] != "-":
            self.screen_width = int(args[3])
            self.screen_height = int(args[4])
        else:
            self.screen_width = None
            self.screen_height = None

        if len(args) > 5:
            self.user_topic = args[5]
        else:
            self.user_topic = None

        if len(args) > 6:
            self.nickname = args[6]
        else:
            self.nickname = None

        if len(args) > 7:
            self.approbation = args[7]
        else:
            self.approbation = None

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
            try:
                self.on_msg(msg)
            except Exception as e:
                # zaloguj chybu
                logging.exception("[" + self.name + "] chyba pri spracovavani spravy " + msg["msg"])
                log = { "log": "chyba pri spracovavani spravy " + msg["msg"] }
                self.publish_message("log", log, "master" )

    def start(self):
        # priprava klienta
        if WEBSOCKETS:
            self.client = mqtt.Client(self.node + "_" + self.name + "_" + self.id, transport="websockets")
        else:
            self.client = mqtt.Client(self.node + "_" + self.name + "_" + self.id)

        # pripojenie k brokeru
        self.client.connect(BROKER_HOST, BROKER_PORT)

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
            logging.exception("[" + self.name + "] chyba pri vykonavani aplikacie")     # repr(e)
            log = { "log": "chyba pri vykonavani aplikacie: " + repr(e) }
            self.publish_message("log", log, "master" )
            #traceback.print_exc()      #TODO malo by byt obsiahnute v logging.exception()
            # skonci
            self.stop()

    def run(self):
        raise NotImplementedError()

    def stop(self):
        # posli spravu o ukoncovani
        logging.info("[" + self.name + "] koncim na uzle " + self.node)
        self.publish_lifecycle_message("quitting")
        self.client.disconnect()


