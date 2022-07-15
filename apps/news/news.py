#!/usr/bin/python3

"""quotes.py: news reader application"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)

# TODO {"url": "https://www.quark.sk/feed/", "stop_string": "&#8230;"}

import sys
import threading
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
    def __init__(self, feed, no_feeds, stop_string, l_title, l_text):
        super().__init__()
        self.entries = feedparser.parse(feed["url"]).entries
        self.no_feeds = no_feeds
        self.stop_string = stop_string
        self.l_title = l_title
        self.l_text = l_text

    def clean_text(self, t):
        s = MLStripper()
        s.feed(t)
        return s.get_data()

    def run(self):
        # read content
        feed_entry = self.entries[random.randint(0, self.no_feeds if self.no_feeds != -1 else len(self.entries)-1)]
        title = feed_entry['title']
        text = feed_entry['summary']
        if self.stop_string is not None:
            text = text[0:text.find(self.stop_string)] + "&#8230;"
        text = self.clean_text(text)
        text = text.strip()
        # change labels
        self.l_title['text'] = title
        self.l_text['text'] = text

class News(base_app.BaseApp):

    def run(self):
        # start processing of mqtt messages
        self.client.loop_start()

        # choose random background color
        colors = ["white", "orange", "yellow", "green"]
        bgcol1 = random.choice(colors)
        bgcol2 = random.choice(colors)

        # show window
        self.top = tkinter.Tk()
        self.top.wm_attributes("-type", "splash")       # no decorations
        self.top.wm_attributes("-fullscreen", True)
        self.top.configure(background=bgcol1)
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
        f_title = tkinter.Frame(self.top, bg=bgcol1)
        f_title.pack(fill=tkinter.X, ipadx=20, ipady=10)
        if "logo" in feed:
            img = tkinter.PhotoImage(file=feed["logo"])
            wrap_len -= img.width()
            canvas = tkinter.Canvas(f_title, width=img.width(), height=img.height(), bg=bgcol1, highlightthickness=0)
            canvas.pack(side=tkinter.LEFT, padx=20)
            canvas.create_image(0, 0, anchor=tkinter.NW, image=img)
        l_title = tkinter.Label(f_title, font=('times', 50), bg=bgcol1, justify=tkinter.LEFT, wraplength=wrap_len)
        # l_title.bind('<Configure>', lambda e: l_title.config(wraplength=l_title.winfo_width()))
        l_title.pack(side=tkinter.LEFT, padx=20, pady=10)

        # text row
        l_text = tkinter.Label(self.top, font=('times', 35), bg=bgcol2, justify=tkinter.LEFT, wraplength=self.top.winfo_screenwidth()-30)
        # l_text.bind('<Configure>', lambda e: l_text.config(wraplength=l_text.winfo_width()))
        l_text.pack(side=tkinter.LEFT, fill=tkinter.BOTH, ipadx=15, ipady=20, expand=True)

        # handle content
        hc = HandleContent(feed, self.config.no_feeds,
                           feed["stop_string"] if "stop_string" in feed else None,
                           l_title, l_text)
        hc.start()

        super().run()

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

