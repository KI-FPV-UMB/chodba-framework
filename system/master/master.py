#!/usr/bin/python3

"""master.py: uzol ma na starosti hlavne lifecycle aplikacii. tato aplikacia sa spusta priamo z os (najlepsie pri starte os), a to len na hlavnom uzle. musi sa spustit ako prva."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import base_app
import app_utils
from app_utils import process_args
from app_utils import run_app

APP_NAME = "master"
APP_TYPE = "system"

APP_ID, NODE_NAME, NICKNAME, APPROBATION, RESPONSE_TOPIC = process_args(sys.argv, APP_NAME, APP_TYPE, "mvagac-X230")

SYSTEM_APPS_PATH = "../../system/"
BACKEND_APPS_PATH = "../../backend-apps/"
FRONTEND_APPS_PATH = "../../frontend-apps/"

WORKSPACES_LAYOUT = dict([
    ('mvagac-X230', app_utils.Rect(0, 0, 1, 1)),
    ('node2', app_utils.Rect(1, 0, 1, 1)),
    ('node3', app_utils.Rect(0, 1, 1, 1)),
    ('node4', app_utils.Rect(1, 1, 1, 1)),
    ('node5', app_utils.Rect(2, 0, 2, 2)),
])

class App:
    def __init__(self):
        self.name = None
        self.type = None
        self.id = None
        self.node = None
        self.status = None
    def __str__(self):
        ret = ""
        if self.name is not None:
            ret += ", " + self.name
        if self.type is not None:
            ret += ", " + self.type
        if self.node is not None:
            ret += ", " + self.node
        if self.status is not None:
            ret += ", " + self.status
        if len(ret) > 0:
            ret = ret[2:]
        return "(" + ret + ")"
    __repr__ = __str__

class Master(base_app.BaseApp):

    def __init__(self):
        self.apps = []

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
        return "master"

    def is_running(self, name, node=None):
        for app in self.apps:
            if app.name == name and (node == None or node == app.node):
                return True
        return False

    def list_offline_apps(self, path):
        ret = []
        for entry in os.listdir(path):
            if os.path.isdir(os.path.join(path, entry)):
                try:
                    app = App()
                    app.name = entry
                    app.type = run_app(path, app.name, 'type')
                    app.demo_time = run_app(path, app.name, 'demotime')
                    # ak je rozpoznana, tak ju pridaj do zoznamu
                    if app.type is not None:
                        ret.append(app.__dict__)       # aby bol objekt serializovatelny do json 
                except Exception as e:
                    print("[" + APP_NAME + "] chyba pri spustani " + app.name + ": " + str(e))
        return ret

    def on_message(self, client, userdata, message):
        sprava = json.loads(message.payload.decode())
        if not "msg" in sprava:
            print("[" + APP_NAME + "] neznamy typ spravy: " + str(sprava))
            return

        if sprava["msg"] == "lifecycle":
            # spravuj zivotny cyklus aplikacie
            app = None
            # nastav stav aplikacie
            for a in self.apps:
                if a.id == sprava["id"]:
                    app = a
                    break
            if app is None:
                app = App()
                app.id = sprava["id"]
                self.apps.append(app)
            if "name" in sprava:
                app.name= sprava["name"]
            if "type" in sprava:
                app.type = sprava["type"]
            if "node" in sprava:
                app.node = sprava["node"]
            if "status" in sprava:
                app.status = sprava["status"]
            # ak je stav quitting, tak vyhod aplikaciu zo zoznamu
            if sprava["status"] == "quitting":
                self.apps.remove(app)
            print("[" + APP_NAME + "] apps: " + str(self.apps))

        if sprava["msg"] == "log":
            # loguj spravu aplikacie
            print("[" + sprava["node"] + "/" + sprava["name"] + "] " + sprava["log"])

        if sprava["msg"] == "info":
            # loguj spravu aplikacie
            print("[" + sprava["name"] + "] " + sprava["type"])
            print("  pub: " + sprava["pub"])
            print("  sub: " + sprava["sub"])

        if sprava["msg"] == "run_backends":
            # pospustaj vsetky backend aplikacie
            apps_list = self.list_offline_apps(BACKEND_APPS_PATH)
            for app in apps_list:
                try:
                    runon = run_app(BACKEND_APPS_PATH, app["name"], 'runon')
                    if runon == '*':
                        # iteruj cez vsetky node_manager-i
                        for nmapp in self.apps:
                            if nmapp.name == "node_manager":
                                # zisti, ci uz na tom uzle bezi
                                if not self.is_running(app["name"], nmapp.node):
                                    # este tam nebezi - spusti
                                    print("[" + APP_NAME + "] spustam " + app["name"] + " na " + nmapp.node)
                                    msg = { 'msg': 'run', 'type':'backend', 'name': app["name"] }
                                    self.client.publish(topic="node/" + nmapp.node, payload=json.dumps(msg), qos=0, retain=False)
                                else:
                                    # uz tam bezi!
                                    print("[" + APP_NAME + "] app " + app["name"] + " je uz na " + nmapp.node + " spustena!")
                    elif runon == '?':
                        # spusti na nahodnom (ak este nikde nebezi)
                        nodes = []
                        for nmapp in self.apps:
                            if nmapp.name == app["name"]:
                                print("[" + APP_NAME + "] app " + app["name"] + " je uz spustena na " + nmapp.node + "!")
                                return
                            if nmapp.name == "node_manager":
                                nodes.append(nmapp.node)
                        # este nebezi, vyber nahodny uzol a spusti
                        node = nodes[random.randint(0, len(nodes)-1)]
                        print("[" + APP_NAME + "] spustam " + app["name"] + " na " + node)
                        msg = { 'msg': 'run', 'type':'backend', 'name': app["name"] }
                        self.client.publish(topic="node/" + node, payload=json.dumps(msg), qos=0, retain=False)
                    else:
                        # spusti na specifikovanom (ak tam este nebezi)
                        if not self.is_running(app["name"], runon):
                            # este tam nebezi - spusti
                            print("[" + APP_NAME + "] spustam " + app["name"] + " na " + runon)
                            msg = { 'msg': 'run', 'type':'backend', 'name': app["name"] }
                            self.client.publish(topic="node/" + runon, payload=json.dumps(msg), qos=0, retain=False)
                        else:
                            # uz tam bezi!
                            print("[" + APP_NAME + "] app " + app["name"] + " je uz na " + runon + " spustena!")
                except Exception as e:
                    print("[" + APP_NAME + "] chyba pri spustani " + app.name + ": " + str(e))

        if sprava["msg"] == "refresh":
            # refreshni status beziacich aplikacii
            for app in self.apps:
                print("[" + APP_NAME + "] refresh stavu " + app.name + " na " + app.node)
                app.status = "refreshing"
                msg = { 'msg': 'status' }
                self.client.publish(topic="app/" + app.name, payload=json.dumps(msg), qos=0, retain=False)

        if sprava["msg"] == "applications":
            if not "response_topic" in sprava:
                return
            apps_list = []
            if not "filter" in sprava or sprava["filter"] == "all":
                if not "type" in sprava or sprava["type"] == "system":
                    apps_list += self.list_offline_apps(SYSTEM_APPS_PATH)
                if not "type" in sprava or sprava["type"] == "backend":
                    apps_list += self.list_offline_apps(BACKEND_APPS_PATH)
                if not "type" in sprava or sprava["type"] == "frontend":
                    apps_list += self.list_offline_apps(FRONTEND_APPS_PATH)
            elif sprava["filter"] == "running":
                for app in self.apps:
                    if not "type" in sprava or sprava["type"] == app.type:
                        apps_list.append(app.__dict__)      # aby bol objekt serializovatelny do json
            resp = { 'msg': 'applications', 'applications': apps_list }
            print(json.dumps(resp))         #TODO
            self.client.publish(topic=sprava["response_topic"], payload=json.dumps(resp), qos=0, retain=False)

        if sprava["msg"] == "workspaces":
            if not "response_topic" in sprava:
                return
            wrkspcs_list = []
            for app in self.apps:
                if app.name == "node_manager":
                    if app.node in WORKSPACES_LAYOUT.keys():
                        WORKSPACES_LAYOUT[app.node].active = True
            for k in WORKSPACES_LAYOUT.keys():
                WORKSPACES_LAYOUT[k].name = k
                wrkspcs_list.append(WORKSPACES_LAYOUT[k].__dict__)
            resp = { 'msg': 'workspaces', 'grid_width': '4', 'grid_height': '2', 'workspaces': wrkspcs_list }
            print(json.dumps(resp))         #TODO
            self.client.publish(topic=sprava["response_topic"], payload=json.dumps(resp), qos=0, retain=False)

        if sprava["msg"] == "approbations":
            if not "response_topic" in sprava:
                return
            apprs_list = [ "AI1", "AI2", "UIN1", "UIN2" ]
            resp = { 'msg': 'approbations', 'approbations': apprs_list }
            print(json.dumps(resp))         #TODO
            self.client.publish(topic=sprava["response_topic"], payload=json.dumps(resp), qos=0, retain=False)

    def run(self):
        self.client.on_message = self.on_message
        self.client.subscribe("master")
        # spusti spracovanie mqtt sprav
        self.client.loop_forever()

    def stop(self):
        # vsetkym rozposli spravu aby koncili..
        for app in self.apps:
            if app.name == APP_NAME:
                continue
            msg = {"msg": "quit"}
            print("[" + APP_NAME + "] vypinam app/" + app.name)
            self.client.publish(topic="app/" + app.name, payload=json.dumps(msg), qos=0, retain=False)
        # skonci
        self.client.disconnect()


if __name__ == '__main__':
    app = Master()
    app.start()
    app.run()


