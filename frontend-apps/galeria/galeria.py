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

SORTED_FILE = "sorted"
NOTITLE_FILE = "notitle"
FONT_PATH = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
#FONT_PATH = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"
#FONT_PATH = "/usr/share/fonts/truetype/ttf-liberation/LiberationSans-Regular.ttf"
FONT_SIZE = 120
FONT_OUTLINE = 3
FS_ENCODING = "utf-8"

class Galeria(base_app.BaseApp):

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
        print("[" + self.name + "]   kreslim ", n, self.files[n])
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
        #sdl2.SDL_UpdateWindowSurface(self.window)

        # dopis nazov adresara
        if not self.notitle:
            nazov_outlined = sdl2.sdlttf.TTF_RenderUTF8_Blended(self.font_outlined, self.folder.encode(FS_ENCODING), sdl2.SDL_Color(0, 0, 0))
            nazov = sdl2.sdlttf.TTF_RenderUTF8_Blended(self.font, self.folder.encode(FS_ENCODING), sdl2.SDL_Color(255, 255, 255))
            # najprv vyrenderuj normalny nazov do outlined
            r = sdl2.SDL_Rect()
            r.x, r.y = FONT_OUTLINE, FONT_OUTLINE
            r.w, r.h = nazov.contents.w, nazov.contents.h
            sdl2.SDL_BlitSurface(nazov, None, nazov_outlined, r)
            # potom ten vysledok (outlined) do okna
            r = sdl2.SDL_Rect()
            r.x, r.y = int(self.window_w/2 - nazov_outlined.contents.w / 2), int(self.window_h - nazov_outlined.contents.h - 10)
            r.w, r.h = nazov_outlined.contents.w, nazov_outlined.contents.h
            sdl2.SDL_BlitSurface(nazov_outlined, None, self.windowsurface, r)

        # update obrazovky (premietnutie zmien)
        sdl2.SDL_RenderPresent(self.renderer)

        #sdl2.SDL_FreeSurface(self.obrazok)             # s tymto to pada
        #sdl2.SDL_FreeSurface(nazov)

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_start()

        # nahodne vyber adresar s obrazkami
        subdirs = [d for d in os.listdir(".") if os.path.isdir(d)]
        #subdirs = [x[0] for x in os.walk(".")]
        if len(subdirs) <= 1:
            log = { "log": "galeria neobsahuje ziadne podadresare s obrazkami!" }
            self.publish_message("log", log, "master" )
            return
        d = random.choice(subdirs)
        print("[" + self.name + "] vyberam ", d)
        self.folder = d[2:]
        self.files = [os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]
        self.sorted = os.path.isfile(os.path.join(d, SORTED_FILE))
        if self.sorted:
            self.files.remove(os.path.join(d, SORTED_FILE))
            self.files.sort()
            self.current = 0                # ak sa obrazky budu zobrazovat sorted, musime si pamatat, ktory bol zobrazeny ako posledny
        self.notitle = os.path.isfile(os.path.join(d, NOTITLE_FILE))
        if self.notitle:
            self.files.remove(os.path.join(d, NOTITLE_FILE))

        # inicializacia SDL2
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
            sys.exit(1)

        if not sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_JPG | sdl2.sdlimage.IMG_INIT_PNG):
            sys.exit(1)

        if sdl2.sdlttf.TTF_Init() <0:
            sys.exit(1)

        # vytvor a zobraz okno (full screen)
        flags = sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_WINDOW_BORDERLESS
        self.window = sdl2.SDL_CreateWindow(b"Galeria", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, 1024, 768, flags)

        # zisti a zapamataj rozmery vytvoreneho okna
        w, h = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_GetWindowSize(self.window, ctypes.byref(w), ctypes.byref(h))
        self.window_w, self.window_h = w.value, h.value

        # priprav pristup na kreslenie do okna
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_SOFTWARE)
        self.windowsurface = sdl2.SDL_GetWindowSurface(self.window)
        self.font = sdl2.sdlttf.TTF_OpenFont(FONT_PATH.encode("ascii"), FONT_SIZE)
        self.font_outlined = sdl2.sdlttf.TTF_OpenFont(FONT_PATH.encode("ascii"), FONT_SIZE)
        sdl2.sdlttf.TTF_SetFontOutline(self.font_outlined, FONT_OUTLINE); 

        # vymaz okno
        sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 0)
        sdl2.SDL_RenderClear(self.renderer)

        # event loop
        self.obrazok = None
        last_draw = time.time()
        self.running = True
        event = sdl2.SDL_Event()
        while self.running:
            self.kresli_obrazok()
            if time.time() - last_draw > self.delay_s:
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
    app.process_args(sys.argv)
    app.start()

