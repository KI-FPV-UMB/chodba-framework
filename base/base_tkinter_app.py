#!/usr/bin/python3

"""base_tkinter_app.py: basic class for Tkinter frontend application."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

import tkinter

from base import base_app

class BaseTkinterApp(base_app.BaseApp):

    def tkinter_init_window(self, title, bgcol):
        self.top = tkinter.Tk()
        self.top.wm_attributes("-type", "splash")  # no decorations
        self.top.wm_attributes("-fullscreen", True)
        self.top.configure(background=bgcol)
        self.window_w, self.window_h = self.top.winfo_screenwidth() - 3, self.top.winfo_screenheight() - 3
        if self.args.screen_width is not None and self.args.screen_height is not None:
            self.window_w, self.window_h = self.args.screen_width - 3, self.args.screen_height - 3
        self.top.geometry("{0}x{1}+0+0".format(self.window_w, self.window_h))
        self.top.focus_set()
        # self.top.resizable(False, False)
        # self.top.update_idletasks()
        # self.top.overrideredirect(True)

