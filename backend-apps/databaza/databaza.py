#!/usr/bin/python3

"""databaza.py: umoznuje perzistenciu udajov pre aplikacie."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# apt-get install mongodb
# je potrebna starsia verzia mongo: pip3 install pymongo==3.4.0

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import pymongo
import base_app
from app_utils import process_args

ENABLED = True
APP_NAME = "databaza"
APP_TYPE = "backend"
DEMO_TIME = 0
RUNON = "chodba-ki01"    #"mvagac-X230"

APP_ID, NODE_NAME, NICKNAME, APPROBATION, USER_TOPIC = process_args(sys.argv, ENABLED, APP_NAME, APP_TYPE, DEMO_TIME, RUNON)

class Databaza(base_app.BaseApp):

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
            self.publish_message("insert-id", resp, msg["src"] )

        elif msg["msg"] == "find":
            # vyber zaznamy z db
            if not "query" in msg:
                log = { "log": "chyba parameter 'query'!" }
                self.publish_message("log", log, "master" )
                return
            try:
                q1 = { "app_name": msg["app_name"] }
                q2 = msg["query"]
                q = { **q1, **q2 }
                if "sort" in msg:
                    if "limit" in msg:
                        cur = self.col.find(q).sort(msg["sort"]).limit(int(msg["limit"]))
                    else:
                        cur = self.col.find(q).sort(msg["sort"])
                else:
                    cur = self.col.find(q)
                l = []
                for doc in cur:
                    del doc["_id"]
                    l.append(doc)
                resp = { "resp": l }
                self.publish_message("resultset", resp, msg["src"] )
            except Exception as e:
                print("[" + self.get_app_name() + "] chyba spustania dotazu " + str(msg["query"]) + ":\n" + repr(e))

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
    app = Databaza()
    app.start()
    app.run()


