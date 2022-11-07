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

from base import base_app

FONT_PATH = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
#FONT_PATH = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"
#FONT_PATH = "/usr/share/fonts/truetype/ttf-liberation/LiberationSans-Regular.ttf"
FONT_SIZE = 70
FS_ENCODING = "utf-8"

class Quotes(base_app.BaseApp):

    def hex_to_rgb(self, hex):
        return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))

    def render_text(self, s, col, x, y, w, h, border = 0, align_h='l', align_v='t'):
        self.text = None
        sdlCol = sdl2.SDL_Color(*self.hex_to_rgb(col[0][1:]))
        st = s.split()
        # text analysis and preparation
        idx = 0
        maxh = 0
        lines = []
        while (idx < len(st)):
            # prepare text line
            pom = ""
            while (idx < len(st)):
                pom += " " + st[idx]
                if self.text is not None:
                    sdl2.SDL_FreeSurface(self.text)
                self.text = sdl2.sdlttf.TTF_RenderUTF8_Blended(self.font, pom[1:].encode(FS_ENCODING), sdlCol)
                if self.text.contents.w >= w - 2*border:
                    break
                idx += 1
            if self.text.contents.w >= w - 2*border:
                # 1 word backwards
                pom = pom.rsplit(' ', 1)[0]
                if self.text is not None:
                    sdl2.SDL_FreeSurface(self.text)
                self.text = sdl2.sdlttf.TTF_RenderUTF8_Blended(self.font, pom[1:].encode(FS_ENCODING), sdlCol)
            lines.append(pom[1:])
            # next line
            maxh += self.text.contents.h

        if align_v == 't':
            yt = y + border
        if align_v == 'm':
            yt = y + h//2 - maxh//2
        if align_v == 'b':
            yt = y + h - border - maxh
        for l in lines:
            if self.text is not None:
                sdl2.SDL_FreeSurface(self.text)
            self.text = sdl2.sdlttf.TTF_RenderUTF8_Blended(self.font, l.encode(FS_ENCODING), sdlCol)
            r = sdl2.SDL_Rect()
            r.y = yt
            if align_h == 'l':
                r.x = x + border
            if align_h == 'r':
                r.x = x + w - border - self.text.contents.w
            if align_h == 'c':
                r.x = x + w//2 - self.text.contents.w//2
            r.w, r.h = self.text.contents.w, self.text.contents.h
            sdl2.SDL_BlitSurface(self.text, None, self.windowsurface, r)
            # next line
            yt += self.text.contents.h

        if self.text is not None:
            sdl2.SDL_FreeSurface(self.text)
        self.text = None

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
        sdl2.ext.init()
        if sdl2.sdlttf.TTF_Init() < 0:
            sys.exit(1)

        # create and show window (full screen)
        flags = sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_WINDOW_BORDERLESS
        self.window = sdl2.ext.Window("Quotes", size=(640, 480), position=(0, 0), flags=flags)
        self.window.show()
        window_w, window_h = self.window.size
        self.windowsurface = self.window.get_surface()

        # clear window and render text
        sdl2.ext.fill(self.windowsurface, sdl2.ext.Color(*self.hex_to_rgb(col[1][1:])))
        self.font = sdl2.sdlttf.TTF_OpenFont(FONT_PATH.encode("ascii"), FONT_SIZE)
        self.render_text(quote, col, 0, 0, window_w, window_h, 15, 'c', 'm')
        self.window.refresh()

        # start processing of mqtt messages
        super().run()

        # event loop
        self.running = True
        event = sdl2.SDL_Event()
        while self.running:
            events = sdl2.ext.get_events()
            for event in events:
                # process events
                if event.type == sdl2.SDL_QUIT:             # event: quit
                    self.running = False
                    break
            sdl2.SDL_Delay(500)                             # in ms

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

