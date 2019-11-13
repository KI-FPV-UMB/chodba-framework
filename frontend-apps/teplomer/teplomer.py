#!/usr/bin/python3

"""teplomer.py: Zobrazovanie nameranej teploty (z databazy)."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base_app
from app_utils import process_args

HIST_DNI = 1                # teplotu kolko dni dozadu zobrazovat

ENABLED = True
APP_NAME = "teplomer"
APP_TYPE = "frontend"
DEMO_TIME = 15

APP_ID, NODE_NAME, NICKNAME, APPROBATION, USER_TOPIC = process_args(sys.argv, ENABLED, APP_NAME, APP_TYPE, DEMO_TIME)

class Teplomer(base_app.BaseApp):

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

    def on_msg(self, msg):
        #print("maaaaaaaaaaaaam")
        #print(str(msg))
        resp = msg["resp"]
        #print(str(resp))
        self.cas = []
        self.teplota = []
        self.vlhkost = []
        for r in resp:
            print(str(r))
            self.cas.append(datetime.datetime.strptime(r["timestamp"], "%Y%m%d%H%M%S%f"))   #.timestamp())
            #self.cas.append(r["timestamp"])
            self.teplota.append(r["temperature"])
            self.vlhkost.append(r["humidity"])
        #print(self.cas)
        #print(self.teplota)
        #print(self.vlhkost)
        # {'src': 'node/mvagac-X230/databaza', 'timestamp': '20191112224659761345', 'resp': [{'timestamp': 2.0, 'humidity': 40.0, 'temperature': 26.0, 'app_name': 'teplota_vlhkost'}, {'timestamp': 3.0, 'humidity': 40.0, 'temperature': 25.0, 'app_name': 'teplota_vlhkost'}, {'timestamp': 4.0, 'humidity': 41.0, 'temperature': 24.0, 'app_name': 'teplota_vlhkost'}, {'timestamp': 5.0, 'humidity': 40.0, 'temperature': 24.0, 'app_name': 'teplota_vlhkost'}], 'app_name': 'databaza', 'msg': 'resultset'}

        self.waiting = False

    def run(self):
        # spusti spracovanie mqtt
        self.client.loop_start()
        # ziskaj data
        hist = (datetime.datetime.now() - datetime.timedelta(HIST_DNI)).strftime('%Y%m%d%H%M%S%f')
        #st = datetime.now().strftime('%Y%m%d%H%M%S%f') #TODO
        #hist = datetime.strftime(datetime.now() - timedelta(HIST_DNI), '%Y%m%d%H%M%S%f')
        msg = { "msg": "find", "app_name": "teplota_vlhkost", "src": self.get_src(), "query": { "timestamp": { "$gt": hist } } }
        #print("posielaaaam", str(msg))          #TODO
        self.client.publish(topic="database", payload=json.dumps(msg), qos=0, retain=False)
        # cakaj
        self.waiting = True
        while self.waiting:
            #plt.pause(1)
            time.sleep(1)

        # zobraz graf
        fig, axt = plt.subplots()
        axt.set_title('teplota za poslednych ' + str(HIST_DNI) + ' dni')
        axt.set_xlim(self.cas[0], self.cas[-1])

        axt.set_ylabel('teplota', color='tab:red')
        axt.plot(self.cas, self.teplota, 'r')
        axt.tick_params(axis='y', labelcolor='tab:red')
        #axt.legend(['teplota'])

        axh = axt.twinx()
        axh.set_ylabel('vlhkost', color='tab:blue')
        axh.plot(self.cas, self.vlhkost, 'b')
        axh.tick_params(axis='y', labelcolor='tab:blue')
        #axh.legend(['vlhkost'])

        xax = axt.get_xaxis()
        xax.set_major_formatter(mdates.DateFormatter("%d.%m"))
        dOd = datetime.date(self.cas[0].year, self.cas[0].month, self.cas[0].day)
        dDo = datetime.date(self.cas[-1].year, self.cas[-1].month, self.cas[-1].day)
        xax.set_ticks([dOd + datetime.timedelta(days=x) for x in range((dDo-dOd).days + 1)])
        _=plt.xticks(rotation=45)

        #plt.plot(self.cas, self.teplota, 'r', self.cas, self.vlhkost, 'b')
        #plt.ylabel('some numbers')

        #plt.tight_layout()
        mng = plt.get_current_fig_manager()
        #mng.frame.Maximize(True)
        #mng.window.state('zoomed')
        mng.resize(*mng.window.maxsize())
        plt.show(block=False)
        # cakaj
        self.running = True
        while self.running:
            #plt.pause(1)
            time.sleep(1)
        # skonci
        plt.close()

    def stop(self):
        # zastav spracovanie mqtt
        super().stop()
        # zrus graf
        self.running = False

if __name__ == '__main__':
    app = Teplomer()
    app.start()
    app.run()


