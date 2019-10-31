#!/usr/bin/python3

"""frontend_planner.py: menezuje spustanie frontend aplikacii na uzloch. ma na starosti to, aby tam vzdy nieco bezalo (t.j. ked nieco skonci, spusti nieco dalsie). tiez zabezpecuje, ze automaticky spustane appky tam budu bezat len urcity cas, potom budu nahradene inymi."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import pymongo
import base_app
from app_utils import process_args

APP_NAME = "database"
APP_TYPE = "app"
DEMO_TIME = 0
RUNON = "mvagac-X230"

APP_ID, NODE_NAME, NICKNAME, APPROBATION, RESPONSE_TOPIC = process_args(sys.argv, APP_NAME, APP_TYPE, DEMO_TIME, RUNON)

class FrontendPlanner(base_app.BaseApp):

    def get_app_name(self):
        return APP_NAME

    def get_app_type(self):
        return APP_TYPE

    def get_app_id(self):
        return APP_ID

    def get_node_name(self):
        return NODE_NAME

    def info_pub(self):
        return ""

    def info_sub(self):
        return ""

    def on_db_message(self, client, userdata, message):
        sprava = json.loads(message.payload.decode())
        if not "msg" in sprava:
            log = { 'msg': 'log', 'name': APP_NAME, 'node': NODE_NAME, 'log': 'neznamy typ spravy: ' + str(sprava) }
            self.client.publish(topic="master", payload=json.dumps(log), qos=0, retain=False)
            return

        if sprava["msg"] == "insert":
            # vloz zaznam do db
            d = { "app_name": sprava["name"], "values": sprava["values"] }
            x = self.col.insert_one(d)
            if not "response_topic" in sprava:
                return
            resp = { 'msg': 'insert-id', 'id': str(x.inserted_id) }
            print(json.dumps(resp))         #TODO
            self.client.publish(topic=sprava["response_topic"], payload=json.dumps(resp), qos=0, retain=False)

    def run(self):
        self.dbc = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.dbc["chodbadb"]
        self.col = self.db["apps"]
        #dblist = dbc.list_database_names()
        #if "chodbadb" not in dblist:
        #      print("Databaza neexistuje, vytvaram...")

        self.client.message_callback_add('database', self.on_db_message)
        self.client.subscribe("database")
        # spracovavaj mqtt spravy
        self.client.loop_forever()


if __name__ == '__main__':
    app = FrontendPlanner()
    app.start()
    app.run()


#TODO mongodb

