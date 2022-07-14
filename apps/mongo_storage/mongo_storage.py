#!/usr/bin/python3

"""mongo_storage.py: umoznuje perzistenciu udajov pre aplikacie."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# apt-get install mongodb

# shell example:
# mongo
#   use chodbadb
#   db.apps.find()
#   db.apps.find().sort({ "timestamp" : 1 }).limit(5)
#   db.apps.find().sort({ "timestamp" : -1 }).limit(5)
#   db.apps.find({"name": "teplota_vlhkost"})

# set PYTHONPATH to project root (chodba-framework)

import sys
import logging
import pymongo
from base import base_app
from base import app_utils

class MongoStorage(base_app.BaseApp):

    def get_specific_topic(self, name: str, node: str) -> list:
        return super().get_specific_topic(name, node) + ["storage"]

    def on_app_msg(self, msg):
        msg_type = msg["header"][app_utils.MSG_TYPE]

        if msg_type == "insert":
            # vloz zaznam do db
            del msg["msg"]
            x = self.col.insert_one(msg)
            resp = { "id": str(x.inserted_id) }
            self.pub_msg("insert-id", resp, msg["src"] )

        elif msg_type == "find":
            # vyber zaznamy z db
            if not "query" in msg:
                log = { "log": "missing parameter 'query'!" }
                self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)
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
                self.pub_msg("resultset", resp, msg["src"] )
            except Exception as e:
                logging.exception("[" + self.name + "] error executing query " + str(msg["query"]))

        else:
            super().on_app_msg(msg)

    def run(self):
        self.dbc = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.dbc["chodbadb"]
        self.col = self.db["apps"]
        #dblist = dbc.list_database_names()
        #if "chodbadb" not in dblist:
        #      logging.info("MongoStorage neexistuje, vytvaram...")

        # start processing of mqtt messages
        self.client.loop_forever()


if __name__ == '__main__':
    app = MongoStorage()
    app.process_args(sys.argv)
    app.start()

