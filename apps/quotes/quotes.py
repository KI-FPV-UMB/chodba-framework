#!/usr/bin/python3

"""quotes.py: quotes application"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)
# apt install fortunes-cs

import sys
import random
import subprocess

import sdl2
import sdl2.ext
import sdl2.sdlttf          # libsdl2-ttf-2.0-0

from base import base_sdl_app

FONT_PATH = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
#FONT_PATH = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"
#FONT_PATH = "/usr/share/fonts/truetype/ttf-liberation/LiberationSans-Regular.ttf"
FONT_SIZE = 70

class Quotes(base_sdl_app.BaseSdlApp):

    def run(self):
        # choose random background color
        colors = [
            ["#000000", "#81b29a"], ["#000000", "#f2cc8f"],
            ["#ffffff", "#3d405b"], ["#000000", "#81b29a"],
            ["#ffffff", "#e07a5f"], ["#ffffff", "#3d405b"],
            ["#000000", "#f4f1de"], ["#ffffff", "#e07a5f"],
        ]
        col = random.choice(colors)

        # prepare text
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

        # sdl init
        self.sdl_init_window()

        # clear window and render text
        sdl2.ext.fill(self.windowsurface, sdl2.ext.Color(*self.hex_to_rgb(col[1][1:])))
        self.font = sdl2.sdlttf.TTF_OpenFont(FONT_PATH.encode("ascii"), FONT_SIZE)
        window_w, window_h = self.window.size
        self.sdl_render_text(quote, col, 0, 0, window_w, window_h, 15, 'c', 'm')
        self.window.refresh()

        # start processing of mqtt messages
        super().run()

        # event loop
        self.sdl_event_loop()

        # release resources
        sdl2.ext.quit()

    def stop(self):
        # stop processing mqtt
        super().stop()
        # stop processing SDL events
        self.running = False

if __name__ == '__main__':
    app = Quotes()
    app.process_args(sys.argv)
    app.start()

