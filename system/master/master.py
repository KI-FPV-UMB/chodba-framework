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
import time
import threading
import base_app
import app_utils


# ak user nespravi ziadnu akciu viac ako USER_TIMEOUT sekund, tak je tato appka vypnuta a nahradena inou
USER_TIMEOUT = 45

# ako casto sa kontroluju (pinguju) aplikacie. aplikacie, ktorych timestamp je starsi ako TIMESTAMP_CHECK su poziadane o status
# aplikacie, ktorych timestamp je starsi ako 3*TIMESTAMP_CHECK su vyhodene zo zoznamu (predpoklada sa, ze ich proces uz nebezi)
TIMESTAMP_CHECK = 60

SYSTEM_APPS_PATH = "../../system/"
BACKEND_APPS_PATH = "../../backend-apps/"
FRONTEND_APPS_PATH = "../../frontend-apps/"

WORKSPACES_LAYOUT = dict([
    ("mvagac-X230", app_utils.Rect(0, 0, 1, 1)),
    ("chodba-ki01", app_utils.Rect(1, 0, 1, 1)),
    ("chodba-ki02", app_utils.Rect(0, 1, 1, 1)),
    ("chodba-ki03", app_utils.Rect(1, 1, 1, 1)),
    ("chodba-ki04", app_utils.Rect(2, 0, 2, 2)),
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
        super(Master, self).__init__()
        self.running_apps = []
        self.quitting = False

    def read_config(self, path):
        if not os.path.isfile(os.path.join(path, "config.json")):
            print("[" + self.name + "] v adresari " + path + " nebol najdeny konfiguracny subor")
            return
        with open(os.path.join(path, "config.json"), "r") as read_file:
            return json.load(read_file)

    def is_running(self, name, node=None):
        for app in self.running_apps:
            if app.name == name and (node == None or node == app.node):
                return True
        return False

    def list_offline_apps(self, path, labels, as_json):
        ret = []
        for entry in os.listdir(path):
            if os.path.isdir(os.path.join(path, entry)):
                app = App()
                # napln atributy podla konfiguracie
                app_config = self.read_config(os.path.join(path, entry))
                has_labels = False
                for k in app_config.keys():
                    setattr(app, k, app_config[k])
                    if k == "labels":
                        has_labels = True
                if app.enabled and (labels is None or (has_labels and (set(labels) & set(app.labels)))):
                    # je povolena a odpoveda poziadavke na labels (ak daka bola)
                    if as_json:
                        ret.append(app.__dict__)       # aby bol objekt serializovatelny do json
                    else:
                        ret.append(app)
        return ret

    def stop_app(self, app):
        # vypni spustene demo
        self.publish_message("quit", {}, "node/" + app.node + "/" + app.name)
        return

    def run_random(self, node):
        # vyber nahodnu aplikaciu (z takych, co maju demo_time > 0)
        apps_list = self.list_offline_apps(FRONTEND_APPS_PATH, ["demo"], False)
        candidates = []
        for a in apps_list:
            if a.demo_time > 0:
                candidates.append(a)
        if len(candidates) == 0:
            print("[" + self.name + "] neboli najdeni ziadni kandidati na spustenie na uzle " + str(node))
            return
        app = candidates[random.randint(0, len(candidates)-1)]
        # spusti aplikaciu na danom node
        print("[" + self.name + "] spustam " + app.name + " na " + node)
        msg2pub = { "type":"frontend", "run": app.name }
        self.publish_message("run", msg2pub, "node/" + node )
        # app je vytvorena z offline apps, takze node nie je definovany - dopln kde to spustame
        app.node = node
        # naplanuj rovno aj jej skoncenie
        t = threading.Timer(app.demo_time, self.stop_app, [app])
        t.start()

    def run_backends(self):
        apps_list = self.list_offline_apps(BACKEND_APPS_PATH, None, False)
        for app in apps_list:
            try:
                if app.runon == "*":
                    # iteruj cez vsetky node_manager-i
                    for nmapp in self.running_apps:
                        if nmapp.name == "node_manager":
                            # zisti, ci uz na tom uzle bezi
                            if not self.is_running(app.name, nmapp.node):
                                # este tam nebezi - spusti
                                print("[" + self.name + "] spustam " + app.name + " na " + nmapp.node)
                                msg2pub = { "type":"backend", "run": app.name }
                                self.publish_message("run", msg2pub, "node/" + nmapp.node )
                            else:
                                # uz tam bezi!
                                print("[" + self.name + "] app " + app.name + " je uz na " + nmapp.node + " spustena!")
                elif app.runon == "?":
                    # spusti na nahodnom (ak este nikde nebezi)
                    nodes = []
                    for nmapp in self.running_apps:
                        if nmapp.name == app.name:
                            print("[" + self.name + "] app " + app.name + " je uz spustena na " + nmapp.node + "!")
                            return
                        if nmapp.name == "node_manager":
                            nodes.append(nmapp.node)
                    # este nebezi, vyber nahodny uzol a spusti
                    node = nodes[random.randint(0, len(nodes)-1)]
                    print("[" + self.name + "] spustam " + app.name + " na " + node)
                    msg2pub = { "type":"backend", "run": app.name }
                    self.publish_message("run", msg2pub, "node/" + node )
                else:
                    # spusti na specifikovanom (ak tam este nebezi)
                    if not self.is_running(app.name, app.runon):
                        # este tam nebezi - spusti
                        print("[" + self.name + "] spustam " + app.name + " na " + app.runon)
                        msg2pub = { "type":"backend", "run": app.name }
                        self.publish_message("run", msg2pub, "node/" + app.runon )
                    else:
                        # uz tam bezi!
                        print("[" + self.name + "] app " + app.name + " je uz na " + app.runon + " spustena!")
            except Exception as e:
                print("[" + self.name + "] chyba pri spustani " + app.name + ": " + str(e))


    def init_node_manager(self, node):
        self.run_random(node)
        # pre istotu spusti backends (ak ma nieco bezat na tomto novom node). to co uz bezi na ostatnych sa nespsusti 2x
        self.run_backends()

    def on_message(self, client, userdata, message):
        msg = json.loads(message.payload.decode())
        if not "msg" in msg:
            print("[" + self.name + "] neznamy typ spravy: " + str(msg))
            return

        if msg["msg"] == "lifecycle":
            # spravuj zivotny cyklus aplikacie
            # podla id zisti, ci uz danu aplikaciu evidujeme
            app = None
            for a in self.running_apps:
                if a.id == msg["id"]:
                    app = a
                    break
            # zaznamenaj stav aplikacie
            if app is None:
                # aplikaciu este neevidujeme (pravdepodobne sa prave spusta)
                app = App()
                app.id = msg["id"]
                app.replaced = False
            for k in msg.keys():
                setattr(app, k, msg[k])
            app.timestamp = time.time()

            # ak je to frontend app tak zisti, ci na danom uzle uz nejaka frontend app nebezi
            if app.status == "starting" and app.type == "frontend":
                is_replacing = False
                for a in self.running_apps:
                    if a.node == app.node and a.type == "frontend":
                        # na uzle uz bezi nejaka frontend app-ka - vypni ju
                        a.replaced = True               # oznac ze je replaced, aby jej vypnutie nesposobilo nasledne spustenie niecoho ineho
                        self.publish_message("quit", {}, "node/" + a.node + "/" + a.name)
                        is_replacing = True
                if is_replacing and (app.nickname is None or app.approbation is None):
                    # nie je user aplikacia a nasilym vytlaca inu beziacu aplikaciu
                    # asi bola spustena mimo bezneho planovania, takze jej treba naplanovat automaticke ukoncenie
                    t = threading.Timer(app.demo_time, self.stop_app, [app])
                    t.start()

            # pridaj appku do zoznamu (ak este nie je)
            if app not in self.running_apps:
                self.running_apps.append(app)
                # ak je to novy node_manager, tak na nom treba hned nieco spustit
                if app.name == "node_manager":
                    t = threading.Timer(3, self.init_node_manager, [app.node])
                    t.start()

            # ak je stav quitting, tak vyhod aplikaciu zo zoznamu
            if app.status == "quitting":
                self.running_apps.remove(app)
                # automaticky tam spusti novu nahodnu appku
                if not self.quitting and not app.replaced:
                    self.run_random(app.node)
            print("[" + self.name + "] apps: ") # + str(self.running_apps))
            for app in self.running_apps:
                print("  " + "{:>10} {:>10}".format(app.name, app.node))
                # type, node, status

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
            self.run_backends()

        elif msg["msg"] == "applications":
            if not "src" in msg:
                print("[" + self.name + "] neznamy odosielatel!")
                return
            # state: all|running
            # type: system|backend|frontend
            # labels: ...
            apps_list = []
            if not "state" in msg or msg["state"] == "all":
                if not "type" in msg or msg["type"] == "system":
                    apps_list += self.list_offline_apps(SYSTEM_APPS_PATH, msg.get("labels", None), True)
                if not "type" in msg or msg["type"] == "backend":
                    apps_list += self.list_offline_apps(BACKEND_APPS_PATH, msg.get("labels", None), True)
                if not "type" in msg or msg["type"] == "frontend":
                    apps_list += self.list_offline_apps(FRONTEND_APPS_PATH, msg.get("labels", None), True)
            elif msg["state"] == "running":
                for app in self.running_apps:
                    if not "type" in msg or msg["type"] == app.type:
                        apps_list.append(app.__dict__)      # aby bol objekt serializovatelny do json
            resp = { "applications": apps_list }
            print(json.dumps(resp), msg["src"])         #TODO
            self.publish_message("applications", resp, msg["src"])

        elif msg["msg"] == "workspaces":
            if not "src" in msg:
                print("[" + self.name + "] neznamy odosielatel!")
                return
            wrkspcs_list = []
            for app in self.running_apps:
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
                print("[" + self.name + "] neznamy odosielatel!")
                return
            apprs_list = [ "AI1", "AI2", "UIN1", "UIN2" ]
            resp = { "approbations": apprs_list }
            print(json.dumps(resp))         #TODO
            self.publish_message("approbations", resp, msg["src"])

        else:
            print("[" + self.name + "] neznamy typ spravy: " + str(msg))

    def check_inactive_users(self):
        last_timestamp_check = time.time()
        while True:
            time.sleep(5)
            # prejdi aplikacie a pri user aplikaciach kontroluj cas poslednej aktivity
            for app in self.running_apps:
                if getattr(app, "nickname", None) is not None and getattr(app, "approbation", None) is not None:
                    # user aplikacia, skontroluj cas poslednej aktivity
                    if time.time() - app.timestamp > USER_TIMEOUT:
                        print("[" + self.name + "] timeout user app " + app.name)
                        self.stop_app(app)
            # v ovela dlhsom intervale pingni vsetky aplikacie, ktore sa davno neozvali (neupdatli lifecycle)
            if time.time() - last_timestamp_check > TIMESTAMP_CHECK:
                last_timestamp_check = time.time()
                for app in self.running_apps:
                    if last_timestamp_check - app.timestamp > 3*TIMESTAMP_CHECK and app.status == "refreshing":
                        # prilis dlho sa neozvali, asi uz nebezia. odstran ich zo zoznamu
                        print("[" + self.name + "] odstranovanie neodpovedajucej app " + app.name)
                        self.running_apps.remove(app)
                        # ak tam nic nebezi, tak tam automaticky spusti novu nahodnu appku
                        if not self.quitting and not app.replaced:
                            obsadeny = False
                            for app2 in self.running_apps:
                                if app2.type == "frontend" and app2.node == app.node:
                                    obsadeny = True
                                    break
                            if not obsadeny:
                                self.run_random(app.node)
                    elif last_timestamp_check - app.timestamp > TIMESTAMP_CHECK:
                        # daj im este sancu - posli poziadavku na refresh
                        print("[" + self.name + "] refresh stavu " + app.name + " na " + app.node)
                        app.status = "refreshing"
                        self.publish_message("status", {}, "node/" + app.node + "/" + app.name)

    def run(self):
        self.client.on_message = self.on_message
        self.client.subscribe("master")

        # vytvor scheduler, ktory bude kontrolovat neaktivne user aplikacie
        t = threading.Thread(target=self.check_inactive_users)
        t.daemon = True
        t.start()

        # spusti spracovanie mqtt sprav
        self.client.loop_forever()

    def stop(self):
        self.quitting = True
        # vsetkym rozposli spravu aby koncili..
        for app in self.running_apps:
            if app.name == self.name:
                continue
            print("[" + self.name + "] vypinam app/" + app.name)
            self.publish_message("quit", {}, "app/" + app.name)
        # skonci
        self.client.disconnect()
        print("[" + self.name + "] koncim na uzle " + self.node)


if __name__ == '__main__':
    app = Master()
    app.start()

