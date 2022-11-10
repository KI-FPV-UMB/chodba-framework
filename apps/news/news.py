#!/usr/bin/python3

"""quotes.py: news reader application"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)
# apt install python3-feedparser

import sys
import threading
import time
import logging
import random
import feedparser

import sdl2
import sdl2.ext
import sdl2.sdlttf          # libsdl2-ttf-2.0-0

from base import base_sdl_app

from io import StringIO
from html.parser import HTMLParser

FONT_PATH = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
#FONT_PATH = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"
#FONT_PATH = "/usr/share/fonts/truetype/ttf-liberation/LiberationSans-Regular.ttf"
FONT_SIZE_TITLE = 100
FONT_SIZE_TEXT = 65

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
    def __init__(self, feed, stop_string, app):
        super().__init__()
        self.entries = feedparser.parse(feed["url"]).entries
        self.no_feeds = app.config.no_feeds
        if self.no_feeds <= 0 or self.no_feeds > len(self.entries):
            self.no_feeds = len(self.entries)
        self.stop_string = stop_string
        self.app = app

    def clean_text(self, t):
        s = MLStripper()
        s.feed(t)
        return s.get_data()

    def set_entry(self, feed_entry):
        # read title and text
        title = feed_entry['title']
        text = feed_entry['summary']
        if self.stop_string is not None:
            text = text[0:text.find(self.stop_string)] + "&#8230;"
        text = self.clean_text(text)
        text = text.strip()
        test = text.replace("\n", " ")

        # display title
        sdl2.ext.fill(self.app.windowsurface, sdl2.ext.Color(*self.app.hex_to_rgb(self.app.col1[1][1:])))
        title_x = 0
        if self.app.logo is not None:
            title_x = self.app.logo.contents.w
        title_h = self.app.sdl_render_text(title, self.app.font_title, self.app.col1[0], title_x, 0, self.app.window_w-title_x, self.app.window_h, 15, 'l', 't')
        title_h += 20
        if self.app.logo is not None:
            if self.app.logo.contents.h > title_h:
                title_h = self.app.logo.contents.h
            r = sdl2.SDL_Rect()
            r.x, r.y = 0, title_h//2 - self.app.logo.contents.h//2
            r.w = self.app.logo.contents.w
            r.h = self.app.logo.contents.h
            sdl2.SDL_BlitSurface(self.app.logo, None, self.app.windowsurface, r)
        # display text
        sdl2.ext.fill(self.app.windowsurface, sdl2.ext.Color(*self.app.hex_to_rgb(self.app.col2[1][1:])), (0, title_h, self.app.window_w, self.app.window_h-title_h))
        self.app.sdl_render_text(text, self.app.font_text, self.app.col2[0], 0, title_h, self.app.window_w, self.app.window_h-title_h, 15, 'l', 't')
        self.app.window.refresh()
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

class News(base_sdl_app.BaseSdlApp):

    def run(self):
        # choose random color (foreground, background)
        colors = [
            ["#000000", "#81b29a"], ["#000000", "#f2cc8f"],
            ["#ffffff", "#3d405b"], ["#000000", "#81b29a"],
            ["#ffffff", "#e07a5f"], ["#ffffff", "#3d405b"],
            ["#000000", "#f4f1de"], ["#ffffff", "#e07a5f"],
        ]
        self.col1 = random.choice(colors)
        colors.remove(self.col1)
        self.col2 = random.choice(colors)

        # sdl init
        self.sdl_ext_init_window('News')

        # clear window and render text
        sdl2.ext.fill(self.windowsurface, sdl2.ext.Color(*self.hex_to_rgb(self.col1[1][1:])))
        self.font_title = sdl2.sdlttf.TTF_OpenFont(FONT_PATH.encode("ascii"), FONT_SIZE_TITLE)
        self.font_text = sdl2.sdlttf.TTF_OpenFont(FONT_PATH.encode("ascii"), FONT_SIZE_TEXT)

        # window content
        feed = self.config.feeds[random.randint(0, len(self.config.feeds) - 1)]

        # title row
        self.logo = None
        if "logo" in feed:
            self.logo = sdl2.sdlimage.IMG_Load(str.encode(feed["logo"]))

        # handle content
        hc = HandleContent(feed, feed["stop_string"] if "stop_string" in feed else None, self)
        hc.start()
        self.window.refresh()

        # start processing of mqtt messages
        super().run()

        # event loop
        # self.sdl_ext_event_loop()
        #sdl2.SDL_Delay(self.config.demo_time*1000)  # in ms
        self.running = True
        while self.running:
            sdl2.SDL_Delay(500)                             # in ms

        # release resources
        if self.logo is not None:
            sdl2.SDL_FreeSurface(self.logo)

        sdl2.ext.quit()

    def stop(self):
        # stop processing mqtt
        super().stop()
        # stop processing SDL events
        self.running = False

if __name__ == '__main__':
    app = News()
    app.process_args(sys.argv)
    app.start()

