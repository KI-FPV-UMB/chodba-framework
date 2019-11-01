#!/usr/bin/python3

"""galeria.py: Slideshow obrazkov z podadresarov. Po spusteni nahodne vyberie podadresar a spusti na nom slideshow."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import random

import sys
import ctypes
import sdl2
import sdl2.sdlimage

import base_app
from app_utils import process_args

APP_NAME = "galeria"
APP_TYPE = "app"
DEMO_TIME = 45

APP_ID, NODE_NAME, NICKNAME, APPROBATION, RESPONSE_TOPIC = process_args(sys.argv, APP_NAME, APP_TYPE, DEMO_TIME)

class SkelSDL(base_app.BaseApp):

    def get_app_name(self):
        return APP_NAME

    def get_app_type(self):
        return APP_TYPE

    def get_app_id(self):
        return APP_ID

    def get_node_name(self):
        return NODE_NAME

    def info_pub(self):
        return ""

    def info_sub(self):
        return ""

    def kresli_obrazok(self):
        # vymaz pozadie
        sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 0)
        sdl2.SDL_RenderClear(self.renderer)
        # nacitaj nahodny obrazok
        n = random.randint(0, len(self.files))
        obrazok = sdl2.sdlimage.IMG_Load(str.encode(self.files[n]))
        # vypocitaj mierku zvacsenia/zmensenia
        aw = obrazok.contents.w / self.window_w
        ah = obrazok.contents.h / self.window_h
        r = sdl2.SDL_Rect()
        a = max(aw, ah)
        nw, nh = obrazok.contents.w / a, obrazok.contents.h / a
        r.x, r.y = int(self.window_w/2 - nw/2), int(self.window_h/2 - nh/2)
        r.w, r.h = int(nw), int(nh)
        # vykresli
        windowsurface = sdl2.SDL_GetWindowSurface(self.window)
        sdl2.SDL_BlitScaled(obrazok, None, windowsurface, r)
        sdl2.SDL_UpdateWindowSurface(self.window)
        sdl2.SDL_FreeSurface(obrazok)
        # update obrazovky (premietnutie zmien)
        sdl2.SDL_RenderPresent(self.renderer)

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_start()

        # nahodne vyber adresar s obrazkami
        subdirs = [x[0] for x in os.walk(".")]
        d = subdirs[random.randint(1, len(subdirs)-1)]
        self.files = [os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]

        # inicializacia SDL2
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
            sys.exit(1)

        if not sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_JPG | sdl2.sdlimage.IMG_INIT_PNG):
            sys.exit(1)

        # vytvor a zobraz okno (full screen)
        flags = sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_WINDOW_BORDERLESS
        self.window = sdl2.SDL_CreateWindow(b"Priklad kreslenia mysou", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, 800, 600, flags)

        # zisti rozmery vytvoreneho okna
        w, h = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_GetWindowSize(self.window, ctypes.byref(w), ctypes.byref(h))
        self.window_w, self.window_h = w.value, h.value

        # priprav pristup na kreslenie do okna (pozadie okna vyfarbi na bielo)
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_SOFTWARE)

        # vykresli nahodny obrazok
        #TODO na zaciatku vypisat nazov adresara
        #TODO toto presunut do cyklu a robit to vzdy po case; postupne geometricky zrychlovat
        self.kresli_obrazok()

        # event loop
        self.running = True
        event = sdl2.SDL_Event()
        while self.running:
            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
                # spracuvaj eventy
                if event.type == sdl2.SDL_QUIT:             # event: quit
                    self.running = False
                    break
            sdl2.SDL_Delay(10)

        # uvolni alokovane zdroje
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

    def stop(self):
        # zastav spracovanie mqtt
        super().stop()
        # zastav spracovanie SDL eventov
        self.running = False


if __name__ == '__main__':
    app = SkelSDL()
    app.start()
    app.run()


