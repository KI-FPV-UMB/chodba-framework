#!/usr/bin/python3

"""news-tkinter.py: news reader application"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)

import sys
import threading
import time
import logging
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


class HandleContent(threading.Thread):
    def __init__(self, feed, no_feeds, stop_string, l_title, l_text, app):
        super().__init__()
        self.entries = feedparser.parse(feed["url"]).entries
        self.no_feeds = no_feeds
        if self.no_feeds <= 0 or self.no_feeds > len(self.entries):
            self.no_feeds = len(self.entries)
        self.stop_string = stop_string
        self.l_title = l_title
        self.l_text = l_text
        self.app = app

    def clean_text(self, t):
        s = MLStripper()
        s.feed(t)
        return s.get_data()

    def set_entry(self, feed_entry):
        # read content
        title = feed_entry['title']
        text = feed_entry['summary']
        if self.stop_string is not None:
            text = text[0:text.find(self.stop_string)] + "&#8230;"
        text = self.clean_text(text)
        text = text.strip()
        test = text.replace("\n", " ")
        # change labels
        self.l_title['text'] = title
        self.l_text['text'] = text
        return len(title) + len(text)

    def run(self):
        if not hasattr(self.app.config, 'demo_time') or int(self.app.config.demo_time) <= 0:
            # display all entries and end
            for i in range(self.no_feeds):
                poc = self.set_entry(self.entries[i])
                if poc > 700:
                    poc = 700
                time.sleep(poc / 20)     # wait accordingly to text length
            self.app.stop()
        else:
            # choose one random entry and wait for scheduled end
            self.set_entry(self.entries[random.randint(0, self.no_feeds-1)])

class News(base_app.BaseApp):

    def run(self):
        # choose random color (foreground, background)
        colors = [
            ["#000", "#81b29a"], ["#000", "#f2cc8f"],
            ["#fff", "#3d405b"], ["#000", "#81b29a"],
            ["#fff", "#e07a5f"], ["#fff", "#3d405b"],
            ["#000", "#f4f1de"], ["#fff", "#e07a5f"],
        ]
        col1 = random.choice(colors)
        colors.remove(col1)
        col2 = random.choice(colors)

        # show window
        self.top = tkinter.Tk()
        self.top.wm_attributes("-type", "splash")       # no decorations
        self.top.wm_attributes("-fullscreen", True)
        self.top.configure(background=col1[1])
        if self.args.screen_width is not None and self.args.screen_height is not None:
            self.top.geometry("{0}x{1}+0+0".format(self.args.screen_width-3, self.args.screen_height-3))
        else:
            self.top.geometry("{0}x{1}+0+0".format(self.top.winfo_screenwidth()-3, self.top.winfo_screenheight()-3))    # fullscreen
#        self.top.resizable(False, False)
#        self.top.update_idletasks()
#        self.top.overrideredirect(True)

        # window content
        wrap_len = self.top.winfo_screenwidth()-70
        feed = self.config.feeds[random.randint(0, len(self.config.feeds) - 1)]

        # title row
        f_title = tkinter.Frame(self.top, bg=col1[1])
        f_title.pack(fill=tkinter.X, ipadx=20, ipady=10)
        if "logo" in feed:
            img = tkinter.PhotoImage(file=feed["logo"])
            wrap_len -= img.width()
            canvas = tkinter.Canvas(f_title, width=img.width(), height=img.height(), bg=col1[1], highlightthickness=0)
            canvas.pack(side=tkinter.LEFT, padx=20)
            canvas.create_image(0, 0, anchor=tkinter.NW, image=img)
        l_title = tkinter.Label(f_title, font=('times', 50), fg=col1[0], bg=col1[1], justify=tkinter.LEFT, wraplength=wrap_len)
        # l_title.bind('<Configure>', lambda e: l_title.config(wraplength=l_title.winfo_width()))
        l_title.pack(side=tkinter.LEFT, padx=20, pady=10)

        # text row
        l_text = tkinter.Label(self.top, font=('times', 35), fg=col2[0], bg=col2[1], justify=tkinter.LEFT, wraplength=self.top.winfo_screenwidth()-30)
        # l_text.bind('<Configure>', lambda e: l_text.config(wraplength=l_text.winfo_width()))
        l_text.pack(side=tkinter.LEFT, fill=tkinter.BOTH, ipadx=15, ipady=20, expand=True)

        # handle content
        hc = HandleContent(feed, self.config.no_feeds,
                           feed["stop_string"] if "stop_string" in feed else None,
                           l_title, l_text, self)
        hc.start()

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
    app = News()
    app.process_args(sys.argv)
    app.start()

