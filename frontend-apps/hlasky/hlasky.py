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
import random
import base_app

class Hlasky(base_app.BaseApp):

    def run(self):
        # spusti spracovanie mqtt
        self.client.loop_start()

        # vyber nahodnu farbu pozadia
        colors = ["white", "orange", "yellow", "green"]
        bgcol = random.choice(colors)

        # zobraz okno
        self.top = tkinter.Tk()
        self.top.wm_attributes("-type", "splash")       # bez dekoracii
        self.top.wm_attributes("-fullscreen", True)
        self.top.configure(background=bgcol)
#        self.top.geometry("{0}x{1}+0+0".format(self.top.winfo_screenwidth()-3, self.top.winfo_screenheight()-3))    # na celu obrazovku
#        self.top.resizable(False, False)
#        self.top.update_idletasks()
#        self.top.overrideredirect(True)

        # nacitaj hlasky zo suboru
        hlasky = []
        with open("hlasky.txt") as fp:
            line = fp.readline()
            while line:
                if not line.startswith("#"):
                    hlasky.append(line)
                line = fp.readline()
        n = random.randint(0, len(hlasky)-1)

        # napln okno obsahom
        msg = tkinter.Message(self.top, text=random.choice(hlasky))
        msg.config(font=('times', 70, 'italic'), bg=bgcol)
        msg.pack(expand=True)                       # aby to bolo vertikalne v strede

        # pracuj
        self.top.mainloop()

    def stop(self):
        # zastav spracovanie mqtt
        super().stop()
        # zrus okno
        self.top.quit()
        #self.top.destroy()

if __name__ == '__main__':
    app = Hlasky()
    app.process_args(sys.argv)
    app.start()

