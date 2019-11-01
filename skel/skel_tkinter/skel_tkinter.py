#!/usr/bin/python3

"""skel_tkinter.py: skel aplikacia pre frontend gui v pythone"""
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

APP_NAME = "skel_tkinter"
APP_TYPE = "app"
DEMO_TIME = 15

APP_ID, NODE_NAME, NICKNAME, APPROBATION, RESPONSE_TOPIC = process_args(sys.argv, APP_NAME, APP_TYPE, DEMO_TIME)

class SkelTkinter(base_app.BaseApp):

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
        # zobraz okno
        self.top = tkinter.Tk()
        self.top.wm_attributes('-type', 'splash')       # bez dekoracii
        self.top.wm_attributes('-fullscreen','true')
#        self.top.geometry("{0}x{1}+0+0".format(self.top.winfo_screenwidth()-3, self.top.winfo_screenheight()-3))    # na celu obrazovku
#        self.top.resizable(False, False)
#        self.top.update_idletasks()
#        self.top.overrideredirect(True)
        # napln okno obsahom
        def tlacidloAkcia():
            tkinter.messagebox.showinfo( "chodba...", "Hello World")
        tlacidlo = tkinter.Button(self.top, text ="Ahoj", command = tlacidloAkcia)
        tlacidlo.pack()
        # pracuj
        self.top.mainloop()

    def stop(self):
        # zastav spracovanie mqtt
        super().stop()
        # zrus okno
        self.top.destroy()

if __name__ == '__main__':
    app = SkelTkinter()
    app.start()
    app.run()


