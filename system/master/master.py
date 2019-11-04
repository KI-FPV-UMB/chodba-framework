#!/usr/bin/python3

"""master.py: uzol ma na starosti hlavne lifecycle aplikacii. tato aplikacia sa spusta priamo z os (najlepsie pri starte os), a to len na hlavnom uzle. musi sa spustit ako prva."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import random
import threading
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
    ("mvagac-X230", app_utils.Rect(0, 0, 1, 1)),
    ("node2", app_utils.Rect(1, 0, 1, 1)),
    ("node3", app_utils.Rect(0, 1, 1, 1)),
    ("node4", app_utils.Rect(1, 1, 1, 1)),
    ("node5", app_utils.Rect(2, 0, 2, 2)),
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

    def get_nickname(self):
        return NICKNAME

    def get_approbation(self):
        return APPROBATION

    def info_pub(self):
        return ""

    def info_sub(self):
        return "master"

    def is_running(self, name, node=None):
        for app in self.apps:
            if app.name == name and (node == None or node == app.node):
                return True
        return False

    def list_offline_apps(self, path, as_json):
        ret = []
        for entry in os.listdir(path):
            if os.path.isdir(os.path.join(path, entry)):
                try:
                    app = App()
                    app.name = entry
                    app.type = run_app(path, app.name, "type")
                    app.demo_time = int(run_app(path, app.name, "demotime"))
                    # ak je rozpoznana, tak ju pridaj do zoznamu
                    if app.type is not None:
                        if as_json:
                            ret.append(app.__dict__)       # aby bol objekt serializovatelny do json
                        else:
                            ret.append(app)
                except Exception as e:
                    print("[" + APP_NAME + "] chyba pri spustani " + app.name + ": " + str(e))
        return ret

    def stop_demo(self, app):
        # vypni spustene demo
        self.publish_message("quit", {}, "node/" + app.node + "/" + app.name)
        return

    def run_random(self, node):
        # vyber nahodnu aplikaciu (z takych, co maju demo_time > 0)
        apps_list = self.list_offline_apps(FRONTEND_APPS_PATH, False)
        candidates = []
        for a in apps_list:
            if a.demo_time > 0:
                candidates.append(a)
        app = candidates[random.randint(0, len(candidates)-1)]
        # spusti aplikaciu na danom node
        print("[" + APP_NAME + "] spustam " + app.name + " na " + node)
        msg2pub = { "type":"frontend", "name": app.name }
        self.publish_message("run", msg2pub, "node/" + node )
        # app je vytvorena z offline apps, takze node nie je definovany - dopln kde to spustame
        app.node = node
        # naplanuj rovno aj jej skoncenie
        t = threading.Timer(app.demo_time, self.stop_demo, [app])
        t.start()

    def on_message(self, client, userdata, message):
        msg = json.loads(message.payload.decode())
        if not "msg" in msg:
            print("[" + APP_NAME + "] neznamy typ spravy: " + str(msg))
            return

        if msg["msg"] == "lifecycle":
            # spravuj zivotny cyklus aplikacie
            app = None
            # nastav parametre aplikacie
            for a in self.apps:
                if a.id == msg["id"]:
                    app = a
                    break
            if app is None:
                app = App()
                app.id = msg["id"]
            if "name" in msg:
                app.name= msg["name"]
            if "type" in msg:
                app.type = msg["type"]
            if "node" in msg:
                app.node = msg["node"]
            if "nickname" in msg:
                app.nickname = msg["nickname"]
            if "approbation" in msg:
                app.approbation = msg["approbation"]
            if "status" in msg:
                app.status = msg["status"]
            # pridaj appku do zoznamu (ak este nie je)
            if app not in self.apps:
                self.apps.append(app)
                # ak je to novy node_manager, tak na nom treba hned nieco spustit
                if msg["name"] == "node_manager":
                    self.run_random(app.node)
            # ak je stav quitting, tak vyhod aplikaciu zo zoznamu
            if msg["status"] == "quitting":
                self.apps.remove(app)
                # automaticky tam spusti novu nahodnu appku
                self.run_random(app.node)
                #TODO tu bude problem, ze ked bude user nieco spustat, tak najprv bude musiet vypnut co tam bezi - a toto hned spusti nieco nove
            print("[" + APP_NAME + "] apps: " + str(self.apps))

        elif msg["msg"] == "log":
            # loguj spravu aplikacie
            src = "???" if not "src" in msg else msg["src"]
            print("[" + src + "] " + msg["log"])

        elif msg["msg"] == "info":
            # loguj spravu aplikacie
            src = "???" if not "src" in msg else msg["src"]
            print("[" + src + "] " + msg["type"])
            print("  pub: " + msg["pub"])
            print("  sub: " + msg["sub"])

        elif msg["msg"] == "run_backends":
            # pospustaj vsetky backend aplikacie
            apps_list = self.list_offline_apps(BACKEND_APPS_PATH, True)
            for app in apps_list:
                try:
                    runon = run_app(BACKEND_APPS_PATH, app["name"], "runon")
                    if runon == "*":
                        # iteruj cez vsetky node_manager-i
                        for nmapp in self.apps:
                            if nmapp.name == "node_manager":
                                # zisti, ci uz na tom uzle bezi
                                if not self.is_running(app["name"], nmapp.node):
                                    # este tam nebezi - spusti
                                    print("[" + APP_NAME + "] spustam " + app["name"] + " na " + nmapp.node)
                                    msg2pub = { "type":"backend", "name": app["name"] }
                                    self.publish_message("run", msg2pub, "node/" + nmapp.node )
                                else:
                                    # uz tam bezi!
                                    print("[" + APP_NAME + "] app " + app["name"] + " je uz na " + nmapp.node + " spustena!")
                    elif runon == "?":
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
                        msg2pub = { "type":"backend", "name": app["name"] }
                        self.publish_message("run", msg2pub, "node/" + node )
                    else:
                        # spusti na specifikovanom (ak tam este nebezi)
                        if not self.is_running(app["name"], runon):
                            # este tam nebezi - spusti
                            print("[" + APP_NAME + "] spustam " + app["name"] + " na " + runon)
                            msg2pub = { "type":"backend", "name": app["name"] }
                            self.publish_message("run", msg2pub, "node/" + runon )
                        else:
                            # uz tam bezi!
                            print("[" + APP_NAME + "] app " + app["name"] + " je uz na " + runon + " spustena!")
                except Exception as e:
                    print("[" + APP_NAME + "] chyba pri spustani " + app.name + ": " + str(e))

        elif msg["msg"] == "refresh":
            # refreshni status beziacich aplikacii
            #TODO bude spustane v pravidelnom intervale. a posli nie vsetkym, ale len tym, ktore sa uz dlho neozvali
            for app in self.apps:
                print("[" + APP_NAME + "] refresh stavu " + app.name + " na " + app.node)
                app.status = "refreshing"
                self.publish_message("status", {}, "app/" + app.name)

        elif msg["msg"] == "applications":
            if not "src" in msg:
                print("[" + APP_NAME + "] neznamy odosielatel!")
                return
            apps_list = []
            if not "filter" in msg or msg["filter"] == "all":
                if not "type" in msg or msg["type"] == "system":
                    apps_list += self.list_offline_apps(SYSTEM_APPS_PATH, True)
                if not "type" in msg or msg["type"] == "backend":
                    apps_list += self.list_offline_apps(BACKEND_APPS_PATH, True)
                if not "type" in msg or msg["type"] == "frontend":
                    apps_list += self.list_offline_apps(FRONTEND_APPS_PATH, True)
            elif msg["filter"] == "running":
                for app in self.apps:
                    if not "type" in msg or msg["type"] == app.type:
                        apps_list.append(app.__dict__)      # aby bol objekt serializovatelny do json
            resp = { "applications": apps_list }
            print(json.dumps(resp))         #TODO
            self.publish_message("applications", resp, msg["src"])

        elif msg["msg"] == "workspaces":
            if not "src" in msg:
                print("[" + APP_NAME + "] neznamy odosielatel!")
                return
            wrkspcs_list = []
            for app in self.apps:
                if app.name == "node_manager":
                    if app.node in WORKSPACES_LAYOUT.keys():
                        WORKSPACES_LAYOUT[app.node].active = True
            for k in WORKSPACES_LAYOUT.keys():
                WORKSPACES_LAYOUT[k].name = k
                wrkspcs_list.append(WORKSPACES_LAYOUT[k].__dict__)
            resp = { "grid_width": "4", "grid_height": "2", "workspaces": wrkspcs_list }
            print(json.dumps(resp))         #TODO
            self.publish_message("workspaces", resp, msg["src"])

        elif msg["msg"] == "approbations":
            if not "src" in msg:
                print("[" + APP_NAME + "] neznamy odosielatel!")
                return
            apprs_list = [ "AI1", "AI2", "UIN1", "UIN2" ]
            resp = { "approbations": apprs_list }
            print(json.dumps(resp))         #TODO
            self.publish_message("approbations", resp, msg["src"])

        else:
            print("[" + APP_NAME + "] neznamy typ spravy: " + str(msg))


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
            print("[" + APP_NAME + "] vypinam app/" + app.name)
            self.publish_message("quit", {}, "app/" + app.name)
        # skonci
        self.client.disconnect()
        print("[" + self.get_app_name() + "] koncim na uzle " + self.get_node_name())


if __name__ == '__main__':
    app = Master()
    app.start()
    app.run()


