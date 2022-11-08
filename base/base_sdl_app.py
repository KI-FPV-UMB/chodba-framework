#!/usr/bin/python3

"""base_sdl_app.py: basic class for SDL frontend application."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

import sys
import sdl2
import ctypes

from base import base_app

FS_ENCODING = "utf-8"

class BaseSdlApp(base_app.BaseApp):

    def sdl_init_window(self):
        sdl2.ext.init()
        if sdl2.sdlttf.TTF_Init() < 0:
            sys.exit(1)

        # create and show window (full screen)
        #TODO asi podla args - ak su tam rozmery obrazovky, tak pouzit tie; ak nie tak fullscreen
        flags = sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_WINDOW_BORDERLESS
        self.window = sdl2.ext.Window("Quotes", size=(640, 480), position=(0, 0), flags=flags)
        self.window.show()
        self.windowsurface = self.window.get_surface()

    def sdl_event_loop(self):
        self.running = True
        event = sdl2.SDL_Event()
        while self.running:
            #TODO raspberry pi workaround (when reading events using get_events(), graphics stop to work)
            # events = sdl2.ext.get_events()
            # for event in events:
            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
                # process events
                if event.type == sdl2.SDL_QUIT:             # event: quit
                    self.running = False
                    break
            self.window.refresh()
            sdl2.SDL_Delay(1000)                            # in ms

    def hex_to_rgb(self, hex):
        return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))

    def sdl_render_text(self, s, col, x, y, w, h, border = 0, align_h='l', align_v='t'):
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
        return maxh
