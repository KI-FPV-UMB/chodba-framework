#!/usr/bin/python3

"""quotes.py: quotes application"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)

import sys
import tkinter
import tkinter.messagebox
import random
import subprocess
from base import base_app

class Hlasky(base_app.BaseApp):

    def run(self):
        # start processing of mqtt messages
        self.client.loop_start()

        # choose random background color
        colors = ["white", "orange", "yellow", "green"]
        bgcol = random.choice(colors)

        # show window
        self.top = tkinter.Tk()
        self.top.wm_attributes("-type", "splash")       # no decorations
        self.top.wm_attributes("-fullscreen", True)
        self.top.configure(background=bgcol)
        if self.args.screen_width is not None and self.args.screen_height is not None:
            self.top.geometry("{0}x{1}+0+0".format(self.args.screen_width-3, self.args.screen_height-3))
        else:
            self.top.geometry("{0}x{1}+0+0".format(self.top.winfo_screenwidth()-3, self.top.winfo_screenheight()-3))    # fullscreen
#        self.top.resizable(False, False)
#        self.top.update_idletasks()
#        self.top.overrideredirect(True)

        r = random.randrange(0, 3)
        if r < 2:
            # quote from fortune
            result = subprocess.run(["/usr/games/fortune", "sk"], stdout=subprocess.PIPE)
            hlaska = result.stdout.decode("utf-8").replace("\t", "")
        else:
            # quote from file
            hlasky = []
            with open("quotes.txt") as fp:
                line = fp.readline()
                while line:
                    if not line.startswith("#"):
                        hlasky.append(line)
                    line = fp.readline()
            #n = random.randint(0, len(hlasky)-1)
            hlaska = random.choice(hlasky)

        # window content
        msg = tkinter.Message(self.top, text=hlaska)
        msg.config(font=('times', 70, 'italic'), bg=bgcol)
        msg.pack(expand=True)          # center vertically

        # work
        self.top.mainloop()

    def stop(self):
        # stop processing mqtt
        super().stop()
        # close window
        self.top.quit()

if __name__ == '__main__':
    app = Hlasky()
    app.process_args(sys.argv)
    app.start()

