#!/usr/bin/python3

"""oznamy_firmy.py: zobrazuje rozne oznamy od firiem (vacsinou ponuky pracovnych miest)"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import tkinter
import tkinter.messagebox
import base_app
from app_utils import process_args

APP_NAME = "oznamy_firmy"
APP_TYPE = "app"

APP_ID, NODE_NAME, NICKNAME, APPROBATION, RESPONSE_TOPIC = process_args(sys.argv, APP_NAME, APP_TYPE)

class OznamyFirmy(base_app.BaseApp):

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
        return ""

    def run(self):
        # spusti spracovanie mqtt
        self.client.loop_start()
        # priprav okno
        self.top = tkinter.Tk()
        self.top.wm_attributes('-type', 'splash')       # bez dekoracii
        self.top.wm_attributes('-fullscreen','true')
        # napln okno obsahom
        lbl = tkinter.Label(self.top, text="Hello", font=("Arial Bold", 50))
        lbl.grid(column=0, row=0)
        def btnAkcia():
            tkinter.messagebox.showinfo( "chodba...", "Hello World")
        btn = tkinter.Button(self.top, text ="Ahoj", command = btnAkcia)
        btn.grid(column=1, row=0)
        # pracuj
        self.top.mainloop()

    def stop(self):
        super().stop()
        self.top.destroy()

if __name__ == '__main__':
    app = OznamyFirmy()
    app.start()
    app.run()


