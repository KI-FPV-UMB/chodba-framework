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

class Quotes(base_app.BaseApp):

    def run(self):
        # choose random background color
        colors = [
            ["#000", "#81b29a"], ["#000", "#f2cc8f"],
            ["#fff", "#3d405b"], ["#000", "#81b29a"],
            ["#fff", "#e07a5f"], ["#fff", "#3d405b"],
            ["#000", "#f4f1de"], ["#fff", "#e07a5f"],
        ]
        col = random.choice(colors)

        # show window
        self.top = tkinter.Tk()
        self.top.wm_attributes("-type", "splash")       # no decorations
        self.top.wm_attributes("-fullscreen", True)
        self.top.configure(background=col[1])
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
            quote = result.stdout.decode("utf-8").replace("\t", "")
        else:
            # quote from file
            quotes = []
            with open("quotes.txt") as fp:
                line = fp.readline()
                while line:
                    if not line.startswith("#"):
                        quotes.append(line)
                    line = fp.readline()
            #n = random.randint(0, len(quotes)-1)
            quote = random.choice(quotes)

        # window content
        msg = tkinter.Message(self.top, text=quote)
        msg.config(font=('times', 70, 'italic'), fg=col[0], bg=col[1])
        msg.pack(expand=True)          # center vertically

        # start processing of mqtt messages
        super().run()

        # work
        self.top.mainloop()

    def stop(self):
        # stop processing mqtt
        super().stop()
        # close window
        self.top.after(0, self.top.destroy)

if __name__ == '__main__':
    app = Quotes()
    app.process_args(sys.argv)
    app.start()

