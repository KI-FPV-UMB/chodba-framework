#!/usr/bin/python3

"""hlasky.py: Zobrazovanie srandovnych hlasok (zo suboru)."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import random
import base_app

FONT_PATH = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
FONT_SIZE = 100
FS_ENCODING = "utf-8"

import sys
import ctypes
import sdl2
import sdl2.sdlimage
import sdl2.sdlttf          # libsdl2-ttf-2.0-0

class Hlasky(base_app.BaseApp):

    def run(self):
        # spusti spracovanie mqtt
        self.client.loop_start()

        # inicializacia SDL2
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
            sys.exit(1)

        if not sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_JPG | sdl2.sdlimage.IMG_INIT_PNG):
            sys.exit(1)

        if sdl2.sdlttf.TTF_Init() <0:
            sys.exit(1)

        # vytvor a zobraz okno (full screen)
        flags = sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_WINDOW_BORDERLESS
        self.window = sdl2.SDL_CreateWindow(b"Hlasky", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, 1024, 768, flags)

        # zisti a zapamataj rozmery vytvoreneho okna
        w, h = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_GetWindowSize(self.window, ctypes.byref(w), ctypes.byref(h))
        self.window_w, self.window_h = w.value, h.value

        # priprav pristup na kreslenie do okna
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_SOFTWARE)
        self.windowsurface = sdl2.SDL_GetWindowSurface(self.window)
        self.font = sdl2.sdlttf.TTF_OpenFont(FONT_PATH.encode("ascii"), FONT_SIZE)

        # nacitaj hlasky zo suboru
        hlasky = []
        with open("hlasky.txt") as fp:
            line = fp.readline()
            while line:
                hlasky.append(line)
                line = fp.readline()
        n = random.randint(0, len(hlasky)-1)
        text = hlasky[n]

        # event loop
        self.running = True
        event = sdl2.SDL_Event()
        while self.running:
            # kresli
            sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 0)
            sdl2.SDL_RenderClear(self.renderer)
            # vypis spravu
            nazov = sdl2.sdlttf.TTF_RenderUTF8_Blended(self.font, text.encode(FS_ENCODING), sdl2.SDL_Color(255, 255, 255))
            r = sdl2.SDL_Rect()
            r.x, r.y = 10, 10
            r.w, r.h = nazov.contents.w, nazov.contents.h
            sdl2.SDL_BlitSurface(nazov, None, self.windowsurface, r)
            sdl2.SDL_RenderPresent(self.renderer)

            # spracuj eventy
            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
                # spracuvaj eventy
                if event.type == sdl2.SDL_QUIT:             # event: quit
                    self.running = False
                    break
            sdl2.SDL_Delay(100)                             # v ms

        # uvolni alokovane zdroje
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()


    def stop(self):
        # zastav spracovanie mqtt
        super().stop()
        # skonci
        self.running = False

if __name__ == '__main__':
    app = Hlasky()
    app.process_args(sys.argv)
    app.start()

