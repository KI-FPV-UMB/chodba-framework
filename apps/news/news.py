#!/usr/bin/python3

"""quotes.py: news reader application"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)

import sys
import tkinter
import tkinter.messagebox
import random
import feedparser
from base import base_app

from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

class News(base_app.BaseApp):

    def clean_text(self, t):
        s = MLStripper()
        s.feed(t)
        return s.get_data()

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

        # , "https://zive.aktuality.sk/rss/najnovsie/"
        feed = self.config.feeds[random.randint(0, len(self.config.feeds) - 1)]
        feed_entry = feedparser.parse(feed["url"]).entries[random.randint(0, self.config.no_feeds)]
        title = feed_entry['title']
        text = feed_entry['summary']
        text = text[0:text.find(feed["stop_string"])] + "&#8230;"
        text = self.clean_text(text)

        # window content
        # title row
        f_title = tkinter.Frame(self.top, bg=bgcol)
        f_title.pack(fill=tkinter.X)
        l_title = tkinter.Label(f_title, text=title, font=('times', 50), bg=bgcol, justify=tkinter.LEFT)
        l_title.bind('<Configure>', lambda e: l_title.config(wraplength=l_title.winfo_width()))
        l_title.pack(padx=50, pady=10) # fill=tkinter.X, padx=5, expand=True
        # text row
        f_text = tkinter.Frame(self.top, bg=bgcol)
        f_text.pack(fill=tkinter.BOTH)
        l_text = tkinter.Label(f_text, text=text, font=('Aerial', 35), bg=bgcol, justify=tkinter.LEFT)
        l_text.bind('<Configure>', lambda e: l_text.config(wraplength=l_text.winfo_width()))
        l_text.pack(padx=50, pady=10) # fill=tkinter.BOTH, padx=5, expand=True

        # work
        self.top.mainloop()

    def stop(self):
        # stop processing mqtt
        super().stop()
        # close window
        self.top.quit()

if __name__ == '__main__':
    app = News()
    app.process_args(sys.argv)
    app.start()

