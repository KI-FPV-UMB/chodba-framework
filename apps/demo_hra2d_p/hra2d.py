#!/usr/bin/python3

"""2D hra"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

import os.path
import logging
import importlib
from types import MethodType
import sys
import ctypes
import sdl2

#TODO scrolling

BIELA = (255, 255, 255)


class AktivnyObjekt:
    def __init__(self, nazov, pozicia, dlazdica_sirka, dlazdica_vyska, bludisko):
        self.data = sdl2.SDL_LoadBMP(str.encode(nazov))
        if not self.data:
            logging.error(sdl2.SDL_GetError())
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

    def zobraz(self):
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
                logging.error(sdl2.SDL_GetError())
            self.dlazdice.append(dlazdica)

        # nacitaj hraca
        self.hrac = Hrac('obrazky/hrac.bmp', (self.sirka/2, self.vyska/2), self.dlazdica_sirka, self.dlazdica_vyska, self)

        # nacitaj prisery
        self.prisery = []
        n = 1
        while os.path.isfile('obrazky/prisera' + str(n) + '.bmp') and os.path.isfile('prisera' + str(n) + '.py'):
            prisera_f = importlib.import_module('prisera' + str(n))
            prisera = AktivnyObjekt('obrazky/prisera1.bmp', prisera_f.pozicia(), self.dlazdica_sirka, self.dlazdica_vyska, self)
            prisera.uprav = MethodType(prisera_f.uprav, prisera)
            self.prisery.append(prisera)
            n += 1


    def rozmer_sirka(self):
        return self.sirka * self.dlazdica_sirka

    def rozmer_vyska(self):
        return self.vyska * self.dlazdica_vyska

    def zobraz(self):
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
            p.zobraz()

        # kresli hraca
        self.hrac.zobraz()

        sdl2.SDL_UpdateWindowSurface(window)
        sdl2.SDL_RenderPresent(renderer)

    def uprav(self):
        # posun hraca
        self.hrac.uprav()
        # posun prisery
        for p in self.prisery:
            p.uprav()


# inicializacia SDL2
if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
    sys.exit(1)

# nacitaj bludisko
bludisko = Bludisko('bludisko.dat')

# priprav okno a kreslenie
window = sdl2.SDL_CreateWindow(b"Hra 2D", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, bludisko.rozmer_sirka(), bludisko.rozmer_vyska(), sdl2.SDL_WINDOW_SHOWN)
windowsurface = sdl2.SDL_GetWindowSurface(window)

renderer = sdl2.SDL_CreateRenderer(window, -1, sdl2.SDL_RENDERER_SOFTWARE)


# event loop
running = True
event = sdl2.SDL_Event()
while running:

    bludisko.uprav()
    bludisko.zobraz()

    while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
        # spracuvaj eventy
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_LEFT:
                bludisko.hrac.dolava = True
            if event.key.keysym.sym == sdl2.SDLK_RIGHT:
                bludisko.hrac.doprava = True
            if event.key.keysym.sym == sdl2.SDLK_UP:
                bludisko.hrac.hore = True
            if event.key.keysym.sym == sdl2.SDLK_DOWN:
                bludisko.hrac.dole = True
        if event.type == sdl2.SDL_KEYUP:
            if event.key.keysym.sym == sdl2.SDLK_LEFT:
                bludisko.hrac.dolava = False
            if event.key.keysym.sym == sdl2.SDLK_RIGHT:
                bludisko.hrac.doprava = False
            if event.key.keysym.sym == sdl2.SDLK_UP:
                bludisko.hrac.hore = False
            if event.key.keysym.sym == sdl2.SDLK_DOWN:
                bludisko.hrac.dole = False
        if event.type == sdl2.SDL_QUIT:
            running = False
            break
    sdl2.SDL_Delay(10)

# uvolni alokovane zdroje
sdl2.SDL_FreeSurface(tile0)
sdl2.SDL_FreeSurface(tile1)
sdl2.SDL_FreeSurface(tile2)

sdl2.SDL_DestroyRenderer(renderer)
sdl2.SDL_DestroyWindow(window)
sdl2.SDL_Quit()

