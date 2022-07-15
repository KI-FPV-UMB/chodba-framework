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
#   db.apps.find({"name": "temp_humi"})

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
            if self.debug:
                 logging.debug("[" + self.config.name + "]  data: " + str(msg["body"]))
            x = self.col.insert_one(msg["body"])
            resp = { "id": str(x.inserted_id) }
            self.pub_msg("insert-id", resp, self.get_specific_topic(msg["header"]["name"], msg["header"]["node"])[0])

        elif msg_type == "find":
            # vyber zaznamy z db
            if not "query" in msg["body"]:
                logging.error("[" + self.config.name + "] missing parameter 'query'!")
                log = { "name": self.config.name, "node": self.node, "level": "error", "log": "missing parameter 'query'!"}
                self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)
                return
            try:
                q1 = { "name": msg["header"]["name"] }
                q2 = msg["body"]["query"]
                if self.debug:
                    logging.debug("[" + self.config.name + "]  query: " + str(q2))
                q = { **q1, **q2 }
                if "sort" in msg["body"]:
                    if "limit" in msg["body"]:
                        cur = self.col.find(q).sort(msg["body"]["sort"]).limit(int(msg["body"]["limit"]))
                    else:
                        cur = self.col.find(q).sort(msg["body"]["sort"])
                else:
                    cur = self.col.find(q)
                l = []
                for doc in cur:
                    del doc["_id"]
                    l.append(doc)
                resp = { "resp": l }
                self.pub_msg("resultset", resp, self.get_specific_topic(msg["header"]["name"], msg["header"]["node"])[0])
            except Exception as e:
                logging.exception("[" + self.config.name + "] error executing query '" + str(msg["query"]) + "': " + repr(e))
                log = { "name": self.config.name, "node": self.node, "level": "error", "log": "error executing query '" + str(msg["query"]) + "': " + repr(e)}
                self.pub_msg("log", log, app_utils.APP_CONTROLLER_TOPIC)

        else:
            super().on_app_msg(msg)

    def run(self):
        super().run()
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

