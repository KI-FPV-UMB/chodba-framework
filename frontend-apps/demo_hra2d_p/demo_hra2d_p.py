#!/usr/bin/python3

"""demo_hra2d_p.py: skel aplikacia pre frontend SDL v pythone"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json

import os.path
import importlib
from types import MethodType
import sys
import ctypes
import sdl2

import base_app
import app_utils

CONTROL_LAYOUT = [
        app_utils.ControlElement("dolava", 0, 1, 2, 2, "<-", "button"),
        app_utils.ControlElement("doprava", 4, 1, 2, 2, "->", "button"),
        app_utils.ControlElement("hore", 2, 0, 2, 2, "^", "button"),
        app_utils.ControlElement("dole", 2, 2, 2, 2, "v", "button"),
]

BIELA = (255, 255, 255)

class AktivnyObjekt:
    def __init__(self, nazov, pozicia, dlazdica_sirka, dlazdica_vyska, bludisko):
        self.data = sdl2.SDL_LoadBMP(str.encode(nazov))
        if not self.data:
            print(sdl2.SDL_GetError())
        # zdroj
        self.frame = 0
        self.sr = sdl2.SDL_Rect()
        self.sr.x, self.sr.y = 0, 0
        self.sr.w, self.sr.h = dlazdica_sirka, dlazdica_vyska
        # ciel
        self.dr = sdl2.SDL_Rect()
        self.dr.w, self.dr.h = dlazdica_sirka, dlazdica_vyska
        self.x, self.y = pozicia[0], pozicia[1]
        # bludisko
        self.bludisko = bludisko

    def zobraz(self, windowsurface):
        self.sr.x = int(self.frame) * self.sr.w
        self.dr.x, self.dr.y = int(self.x * self.dr.w), int(self.y * self.dr.h)
        sdl2.SDL_BlitSurface(self.data, self.sr, windowsurface, self.dr)

class Hrac(AktivnyObjekt):
    def __init__(self, nazov, pozicia, dlazdica_sirka, dlazdica_vyska, bludisko):
        super().__init__(nazov, pozicia, dlazdica_sirka, dlazdica_vyska, bludisko)
        # pohyb
        self.delta_pohyb = 0.05
        self.dolava = False
        self.doprava = False
        self.hore = False
        self.dole = False

    def uprav(self):
        if self.dolava or self.doprava or self.hore or self.dole:
            self.frame += 0.1
            if self.frame >= 3:
                self.frame = 0
        if self.dolava:
            self.x -= self.delta_pohyb
        if self.doprava:
            self.x += self.delta_pohyb
        if self.hore:
            self.y -= self.delta_pohyb
        if self.dole:
            self.y += self.delta_pohyb

class Bludisko:
    def __init__(self, nazov):
        # nacitaj rozmery
        subor = open(nazov, 'r')
        self.sirka, self.vyska = [ int(x) for x in subor.readline().split() ]
        self.dlazdica_sirka, self.dlazdica_vyska = [ int(x) for x in subor.readline().split() ]

        # nacitaj data
        self.data = [[0] * self.sirka for i in range(self.vyska)]
        for y in range(self.vyska):
            riadok = subor.readline()
            x = 0
            for t in riadok.split():
                self.data[y][x] = int(t)
                x += 1

        # nacitaj dlazdice
        self.dlazdice = []
        n = int(subor.readline())
        for i in range(0, n):
            naz = subor.readline()
            s = "obrazky/" + naz.rstrip()
            dlazdica = sdl2.SDL_LoadBMP(str.encode(s))
            if not dlazdica:
                print(sdl2.SDL_GetError())
            self.dlazdice.append(dlazdica)

        # nacitaj hraca
        self.hrac = Hrac("obrazky/hrac.bmp", (self.sirka/2, self.vyska/2), self.dlazdica_sirka, self.dlazdica_vyska, self)

        # nacitaj prisery
        self.prisery = []
        n = 1
        while os.path.isfile("obrazky/prisera" + str(n) + ".bmp") and os.path.isfile("prisera" + str(n) + ".py"):
            prisera_f = importlib.import_module("prisera" + str(n))
            prisera = AktivnyObjekt("obrazky/prisera1.bmp", prisera_f.pozicia(), self.dlazdica_sirka, self.dlazdica_vyska, self)
            prisera.uprav = MethodType(prisera_f.uprav, prisera)
            self.prisery.append(prisera)
            n += 1

    def rozmer_sirka(self):
        return self.sirka * self.dlazdica_sirka

    def rozmer_vyska(self):
        return self.vyska * self.dlazdica_vyska

    def zobraz(self, window, renderer, windowsurface):
        sdl2.SDL_SetRenderDrawColor(renderer, BIELA[0], BIELA[1], BIELA[2], 0)
        sdl2.SDL_RenderClear(renderer)
 
        r = sdl2.SDL_Rect()
        r.x, r.y = 0, 0
        r.w, r.h = self.dlazdica_sirka, self.dlazdica_vyska

        # kresli dlazdice
        for y in range(self.vyska):
            for x in range(self.sirka):
                r.x = x * self.dlazdica_sirka
                r.y = y * self.dlazdica_vyska
                d = self.data[y][x]
                sdl2.SDL_BlitSurface(self.dlazdice[d], None, windowsurface, r)

        # kresli prisery
        for p in self.prisery:
            p.zobraz(windowsurface)

        # kresli hraca
        self.hrac.zobraz(windowsurface)

        sdl2.SDL_UpdateWindowSurface(window)
        sdl2.SDL_RenderPresent(renderer)

    def uprav(self):
        # posun hraca
        self.hrac.uprav()
        # posun prisery
        for p in self.prisery:
            p.uprav()


class DemoHra2Dp(base_app.BaseApp):

    def on_msg(self, msg):
        if msg["msg"] == "control_action":
            if msg["type"] == "keydown":
                if msg["name"] == "hore":
                    self.bludisko.hrac.hore = True
                if msg["name"] == "dole":
                    self.bludisko.hrac.dole = True
                if msg["name"] == "dolava":
                    self.bludisko.hrac.dolava= True
                if msg["name"] == "doprava":
                    self.bludisko.hrac.doprava = True
            if msg["type"] == "keyup":
                if msg["name"] == "hore":
                    self.bludisko.hrac.hore = False
                if msg["name"] == "dole":
                    self.bludisko.hrac.dole = False
                if msg["name"] == "dolava":
                    self.bludisko.hrac.dolava= False
                if msg["name"] == "doprava":
                    self.bludisko.hrac.doprava = False
            self.publish_lifecycle_message("playing")
        else:
            super.on_msg(msg)

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_start()

        # oznam pozadovany layout klavesnice
        if self.user_topic is not None:
            ctrls_list = []
            for ctrl in CONTROL_LAYOUT:
                ctrls_list.append(ctrl.__dict__)
            resp = { "grid_width": "6", "grid_height": "4", "type": "static", "control_elements": ctrls_list }
            print(json.dumps(resp))            #TODO
            self.publish_message("control_layout", resp, self.user_topic)

        # inicializacia SDL2
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
            sys.exit(1)

        # nacitaj bludisko
        self.bludisko = Bludisko("bludisko.dat")

        # priprav okno a kreslenie
        flags = sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_WINDOW_BORDERLESS
        window = sdl2.SDL_CreateWindow(b"Hra 2D", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, self.bludisko.rozmer_sirka(), self.bludisko.rozmer_vyska(), flags)
        windowsurface = sdl2.SDL_GetWindowSurface(window)

        # priprav pristup na kreslenie do okna (pozadie okna vyfarbi na bielo)
        renderer = sdl2.SDL_CreateRenderer(window, -1, sdl2.SDL_RENDERER_SOFTWARE)
        sdl2.SDL_SetRenderDrawColor(renderer, 255, 255, 255, 0)                         # nastav farbu kreslenia
        sdl2.SDL_RenderClear(renderer)                                                  # vymaz celu obrazovku danou farbou
        sdl2.SDL_RenderPresent(renderer)                                                # update obrazovky (premietnutie zmien)

        # event loop
        self.running = True
        event = sdl2.SDL_Event()
        while self.running:

            self.bludisko.uprav()
            self.bludisko.zobraz(window, renderer, windowsurface)

            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
                # spracuvaj eventy
                if event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_LEFT:
                        self.bludisko.hrac.dolava = True
                    if event.key.keysym.sym == sdl2.SDLK_RIGHT:
                        self.bludisko.hrac.doprava = True
                    if event.key.keysym.sym == sdl2.SDLK_UP:
                        self.bludisko.hrac.hore = True
                    if event.key.keysym.sym == sdl2.SDLK_DOWN:
                        self.bludisko.hrac.dole = True
                if event.type == sdl2.SDL_KEYUP:
                    if event.key.keysym.sym == sdl2.SDLK_LEFT:
                        self.bludisko.hrac.dolava = False
                    if event.key.keysym.sym == sdl2.SDLK_RIGHT:
                        self.bludisko.hrac.doprava = False
                    if event.key.keysym.sym == sdl2.SDLK_UP:
                        self.bludisko.hrac.hore = False
                    if event.key.keysym.sym == sdl2.SDLK_DOWN:
                        self.bludisko.hrac.dole = False
                if event.type == sdl2.SDL_QUIT:
                    self.running = False
                    break

            sdl2.SDL_Delay(10)

        # uvolni alokovane zdroje
        sdl2.SDL_DestroyRenderer(renderer)
        sdl2.SDL_DestroyWindow(window)
        sdl2.SDL_Quit()


    def stop(self):
        # zastav spracovanie mqtt
        super().stop()
        # zastav spracovanie SDL eventov
        self.running = False


if __name__ == '__main__':
    app = DemoHra2Dp()
    app.process_args(sys.argv)
    app.start()

