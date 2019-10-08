#!/usr/bin/python3

# PYTHONPATH musi odkazoat na absolutnu cestu k .../chodba-framework/base

# tato aplikacia sa spusta priamo z os (vzdy pri starte os); a to len na hlavnom uzle. musi sa spustit ako prva

import sys
import os
import socket
import subprocess
import paho.mqtt.client as mqtt
import json
import base_app

APP_NAME = "frontend_planner"
APP_TYPE = "app"

#TODO len pre pokus...

BACKEND_APPS_PATH = "../../backend-apps/"
FRONTEND_APPS_PATH = "../../frontend-apps/"

# na poziadnie oznam typ
if len(sys.argv) == 2 and sys.argv[1]=="type":
    print(APP_TYPE)
    sys.exit(1)

# na poziadnie oznam, kde sa ma spustit: * na vsetkych, ? na lubovolnom, <nazov> na konkretnom
if len(sys.argv) == 2 and sys.argv[1]=="runon":
    # zobraz informaciu, na ktorych uzloch sa ma backend spustat
    print("mvagac-X230")        # nazov master uzla
    sys.exit(1)

# ako parameter sa ocakava nazov uzla, kde sa backend spusta
NODE_NAME = socket.gethostname()
print("nazov uzla: " + NODE_NAME)

class App:
    def __init__(self):
        self.type = "?"
        self.node = "?"
        self.status = "?"
    def __str__(self):
        return "(" + self.type + ", " + self.node + ", " + self.status + ")"
    __repr__ = __str__

class Master(base_app.BaseApp):

    def __init__(self):
        self.apps = {}

    def get_app_name(self):
        return APP_NAME

    def get_app_type(self):
        return APP_TYPE

    def info_pub(self):
        return ""

    def info_sub(self):
        return "master"

    def list_offline_apps(self, path):
        ret = []
        for entry in os.listdir(path):
            if os.path.isdir(os.path.join(path, entry)):
                ret.append(entry)
                p = os.path.join(path, entry)
                # test pre python app
                f = os.path.join(p, entry) + ".py"
                print("2:" + f)
                if os.path.isfile(f):
                    app_type = subprocess.run([os.path.join(path, entry), 'type'], stdout=subprocess.PIPE)
                    print(app_type.stdout)
                # TODO nezabudnut aj na ostatny typy aplikacii (Java, ...)
        return ret

    def on_message(self, client, userdata, message):
        sprava = json.loads(message.payload.decode())
        if not "msg" in sprava:
            print("[master] neznamy typ spravy: " + str(sprava))
            return

        if sprava["msg"] == "lifecycle":
            # spravuj zivotny cyklus aplikacie
            app_name = sprava["app"]
            # nastav stav aplikacie
            if not app_name in self.apps:
                self.apps[app_name] = App()
            if "type" in sprava:
                self.apps[app_name].type = sprava["type"]
            if "node" in sprava:
                self.apps[app_name].node = sprava["node"]
            if "status" in sprava:
                self.apps[app_name].status = sprava["status"]
            # ak je stav quitting, tak vyhod aplikaciu zo zoznamu
            if sprava["status"] == "quitting":
                del self.apps[app_name]
            print("[master] apps: " + str(self.apps))

        if sprava["msg"] == "log":
            # loguj spravu aplikacie
            print("[" + sprava["app"] + "] " + sprava["log"])

        if sprava["msg"] == "info":
            # loguj spravu aplikacie
            print("[" + sprava["app"] + "] " + sprava["type"])
            print("  pub: " + sprava["pub"])
            print("  sub: " + sprava["sub"])

        if sprava["msg"] == "applications":
            if not "response_topic" in sprava:
                return
            if not "filter" in sprava or sprava["filter"] == "all":
                apps_list = []
                if not "type" in sprava or sprava["type"] == "backend":
                    apps_list += self.list_offline_apps(BACKEND_APPS_PATH)
                if not "type" in sprava or sprava["type"] == "frontend":
                    apps_list += self.list_offline_apps(FRONTEND_APPS_PATH)
            elif sprava["filter"] == "running":
                apps_list = list(self.apps.keys())
                #TODO odfiltrovat podla "type" (ak je): frontend|backend
            print(apps_list)    #TODO posli zoznam ale aj s info o kazdej appke: typ; plus o beziacej: kde bezi
            resp = { 'msg': 'applications' }
            self.client.publish(topic=sprava["response_topic"], payload=json.dumps(resp), qos=0, retain=False)

        if sprava["msg"] == "workspaces":
            if not "response_topic" in sprava:
                return
            #TODO sprav zoznam workspaces podla beziacich node_manager

    def run(self):
        self.client.on_message = self.on_message
        self.client.subscribe("master")
        # cakaj
        self.client.loop_forever()


if __name__ == '__main__':
    app = Master()
    app.start()
    app.run()


