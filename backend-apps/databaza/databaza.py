#!/usr/bin/python3

"""frontend_planner.py: menezuje spustanie frontend aplikacii na uzloch. ma na starosti to, aby tam vzdy nieco bezalo (t.j. ked nieco skonci, spusti nieco dalsie). tiez zabezpecuje, ze automaticky spustane appky tam budu bezat len urcity cas, potom budu nahradene inymi."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# je potrebna starsia verzia mongo: pip3 install pymongo==3.4.0

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import pymongo
import base_app
from app_utils import process_args

APP_NAME = "databaza"
APP_TYPE = "backend"
DEMO_TIME = 0
RUNON = "walle09"    #"mvagac-X230"

APP_ID, NODE_NAME, NICKNAME, APPROBATION, USER_TOPIC = process_args(sys.argv, APP_NAME, APP_TYPE, DEMO_TIME, RUNON)

class FrontendPlanner(base_app.BaseApp):

    def get_app_name(self):
        return APP_NAME

    def get_app_type(self):
        return APP_TYPE

    def get_app_id(self):
        return APP_ID

    def get_node_name(self):
        return NODE_NAME

    def get_nickname(self):
        return NICKNAME

    def get_approbation(self):
        return APPROBATION

    def info_pub(self):
        return ""

    def info_sub(self):
        return ""

    def on_db_message(self, client, userdata, message):
        msg = json.loads(message.payload.decode())
        if not "msg" in msg:
            log = { "log": "neznamy typ spravy: " + str(msg) }
            self.publish_message("log", log, "master" )
            return

        if msg["msg"] == "insert":
            # vloz zaznam do db
            del msg["msg"]
            x = self.col.insert_one(msg)
            resp = { "id": str(x.inserted_id) }
            print(json.dumps(resp))         #TODO
            self.publish_message("insert-id", resp, msg["src"] )

        elif msg["msg"] == "find":
            # vyber zaznamy z db
            q1 = { "app_name": msg["app_name"] }
            q2 = msg["query"]
            q = { **q1, **q2 }
            if "sort" in msg:
                if "limit" in msg:
                    resp = self.col.find(q).sort(msg["sort"]).limit(int(msg["limit"]))
                else:
                    resp = self.col.find(q).sort(msg["sort"])
            else:
                resp = self.col.find(q)
            print(json.dumps(resp))         #TODO
            self.publish_message("resultset", resp, msg["src"] )

        else:
            super.on_msg(msg)

    def run(self):
        self.dbc = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.dbc["chodbadb"]
        self.col = self.db["apps"]
        #dblist = dbc.list_database_names()
        #if "chodbadb" not in dblist:
        #      print("Databaza neexistuje, vytvaram...")

        self.client.message_callback_add("database", self.on_db_message)
        self.client.subscribe("database")
        # spracovavaj mqtt spravy
        self.client.loop_forever()


if __name__ == '__main__':
    app = FrontendPlanner()
    app.start()
    app.run()


#TODO mongodb


