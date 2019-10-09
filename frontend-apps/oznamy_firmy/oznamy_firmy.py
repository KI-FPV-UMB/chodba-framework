#!/usr/bin/python3

"""oznamy_firmy.py: zobrazuje rozne oznamy od firiem (vacsinou ponuky pracovnych miest)"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import random
import socket
import paho.mqtt.client as mqtt
import json
import tkinter
import tkinter.messagebox
import base_app

APP_NAME = "oznamy_firmy"
APP_TYPE = "app"
APP_ID = hex(random.getrandbits(128))[2:-1]

# na poziadnie oznam typ
if len(sys.argv) == 2 and sys.argv[1]=="type":
    print(APP_TYPE)
    sys.exit(1)

# nazov uzla je dany hostname
NODE_NAME = socket.gethostname()
print("[" + APP_NAME + "] spustam na uzle " + NODE_NAME)

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
        # zobraz okno
        self.top = tkinter.Tk()
        self.top.wm_attributes('-type', 'splash')       # bez dekoracii
        self.top.wm_attributes('-fullscreen','true')
#        self.top.geometry("{0}x{1}+0+0".format(self.top.winfo_screenwidth()-3, self.top.winfo_screenheight()-3))    # na celu obrazovku
#        self.top.resizable(False, False)
#        self.top.update_idletasks()
#        self.top.overrideredirect(True)
        def tlacidloAkcia():
            tkinter.messagebox.showinfo( "chodba...", "Hello World")
        tlacidlo = tkinter.Button(self.top, text ="Ahoj", command = tlacidloAkcia)
        tlacidlo.pack()
        self.top.mainloop()

    def stop(self):
        super().stop()
        self.top.destroy()

if __name__ == '__main__':
    app = OznamyFirmy()
    app.start()
    app.run()


