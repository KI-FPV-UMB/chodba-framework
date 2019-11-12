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
import time

import sys
import ctypes
import sdl2
import sdl2.sdlimage
import sdl2.sdlttf          # libsdl2-ttf-2.0-0

import base_app
from app_utils import process_args

SORTED_FILE = "sorted"
FONT_PATH = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
#FONT_PATH = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"
#FONT_PATH = "/usr/share/fonts/truetype/ttf-liberation/LiberationSans-Regular.ttf"
FONT_SIZE = 120
FS_ENCODING = "iso-8859-2"
DELAY_S = 1.5

ENABLED = True
APP_NAME = "galeria"
APP_TYPE = "frontend"
DEMO_TIME = 45

APP_ID, NODE_NAME, NICKNAME, APPROBATION, USER_TOPIC = process_args(sys.argv, ENABLED, APP_NAME, APP_TYPE, DEMO_TIME)

class Galeria(base_app.BaseApp):

    def get_app_name(self):
        return APP_NAME

    def get_app_type(self):
        return APP_TYPE

    def get_app_id(self):
        return APP_ID

    def get_node_name(self):
        return NODE_NAME

    def get_demo_time(self):
        return DEMO_TIME

    def get_nickname(self):
        return NICKNAME

    def get_approbation(self):
        return APPROBATION

    def info_pub(self):
        return ""

    def info_sub(self):
        return ""

    def dalsi_obrazok(self):
        # nacitaj obrazok
        if self.sorted:
            # v poradi
            n = self.current
            self.current += 1
            if self.current >= len(self.files):
                self.current = 0
        else:
            # nahodny
            n = random.randint(0, len(self.files)-1)
        #print("kreslim", n, self.files[n])
        self.obrazok = sdl2.sdlimage.IMG_Load(str.encode(self.files[n]))

    def kresli_obrazok(self):
        if self.obrazok is None:
            self.dalsi_obrazok()
        # vymaz pozadie
        sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 0)
        sdl2.SDL_RenderClear(self.renderer)
        # vypocitaj mierku zvacsenia/zmensenia
        aw = self.obrazok.contents.w / self.window_w
        ah = self.obrazok.contents.h / self.window_h
        r = sdl2.SDL_Rect()
        a = max(aw, ah)
        nw, nh = self.obrazok.contents.w / a, self.obrazok.contents.h / a
        r.x, r.y = int(self.window_w/2 - nw/2), int(self.window_h/2 - nh/2)
        r.w, r.h = int(nw), int(nh)
        # vykresli
        sdl2.SDL_BlitScaled(self.obrazok, None, self.windowsurface, r)
        sdl2.SDL_UpdateWindowSurface(self.window)
        #sdl2.SDL_FreeSurface(self.obrazok)             # s tymto to pada
        # update obrazovky (premietnutie zmien)
        sdl2.SDL_RenderPresent(self.renderer)

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_start()

        # nahodne vyber adresar s obrazkami
        subdirs = [x[0] for x in os.walk(".")]
        if len(subdirs) <= 1:
            log = { "log": "galeria neobsahuje ziadne podadresare s obrazkami!" }
            self.publish_message("log", log, "master" )
            return
        d = subdirs[random.randint(1, len(subdirs)-1)]
        self.files = [os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]
        self.sorted = os.path.isfile(os.path.join(d, SORTED_FILE))
        if self.sorted:
            self.files.remove(os.path.join(d, SORTED_FILE))
            self.files.sort()
            self.current = 0                # ak sa obrazky budu zobrazovat sorted, musime si pamatat, ktory bol zobrazeny ako posledny

        # inicializacia SDL2
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
            sys.exit(1)

        if not sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_JPG | sdl2.sdlimage.IMG_INIT_PNG):
            sys.exit(1)

        if sdl2.sdlttf.TTF_Init() <0:
            sys.exit(1)

        # vytvor a zobraz okno (full screen)
        flags = sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_WINDOW_BORDERLESS
        self.window = sdl2.SDL_CreateWindow(b"Galeria", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, 800, 600, flags)

        # zisti a zapamataj rozmery vytvoreneho okna
        w, h = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_GetWindowSize(self.window, ctypes.byref(w), ctypes.byref(h))
        self.window_w, self.window_h = w.value, h.value

        # priprav pristup na kreslenie do okna
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_SOFTWARE)
        self.windowsurface = sdl2.SDL_GetWindowSurface(self.window)

        # vymaz okno
        sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 0)
        sdl2.SDL_RenderClear(self.renderer)

        # vypis nazov adresara
        font = sdl2.sdlttf.TTF_OpenFont(FONT_PATH.encode("ascii"), FONT_SIZE)
        nazov = sdl2.sdlttf.TTF_RenderText_Solid(font, d[2:].encode(FS_ENCODING), sdl2.SDL_Color(255, 255, 255))
        r = sdl2.SDL_Rect()
        r.x, r.y = int(self.window_w/2 - nazov.contents.w / 2), int(self.window_h/2 - nazov.contents.h / 2)
        r.w, r.h = nazov.contents.w, nazov.contents.h
        sdl2.SDL_BlitSurface(nazov, None, self.windowsurface, r)
        sdl2.SDL_FreeSurface(nazov)
        sdl2.SDL_RenderPresent(self.renderer)

        # event loop
        self.obrazok = None
        last_draw = time.time()
        self.running = True
        event = sdl2.SDL_Event()
        while self.running:
            self.kresli_obrazok()
            if time.time() - last_draw > DELAY_S:
                self.dalsi_obrazok()
                last_draw = time.time()
                # TODO cas pauzy postupne skracovat

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
        # zastav spracovanie SDL eventov
        self.running = False


if __name__ == '__main__':
    app = Galeria()
    app.start()
    app.run()


