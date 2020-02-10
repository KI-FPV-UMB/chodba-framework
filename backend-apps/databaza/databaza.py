#!/usr/bin/python3

"""databaza.py: umoznuje perzistenciu udajov pre aplikacie."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# apt-get install mongodb
# je potrebna starsia verzia mongo: pip3 install pymongo==3.4.0

# praca s db v shelli:
# mongo
#   use chodbadb
#   db.apps.find()
#   db.apps.find().sort({ "timestamp" : 1 }).limit(5)
#   db.apps.find().sort({ "timestamp" : -1 }).limit(5)
#   db.apps.find({"name": "teplota_vlhkost"})


# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import pymongo
import base_app

class Databaza(base_app.BaseApp):

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
                q1 = { "name": msg["name"] }
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
                print("[" + self.name + "] chyba spustania dotazu " + str(msg["query"]) + ":\n" + repr(e))

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
    app.process_args(sys.argv)
    app.start()

