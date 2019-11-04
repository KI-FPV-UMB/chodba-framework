#!/usr/bin/python3

"""skel_sdl.py: skel aplikacia pre frontend SDL v pythone"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json

import sys
import ctypes
import sdl2

import base_app
from app_utils import process_args

APP_NAME = "skel_sdl"
APP_TYPE = "frontend"
DEMO_TIME = 15

APP_ID, NODE_NAME, NICKNAME, APPROBATION, USER_TOPIC = process_args(sys.argv, APP_NAME, APP_TYPE, DEMO_TIME)

class SkelSDL(base_app.BaseApp):

    def get_app_name(self):
        return APP_NAME

    def get_app_type(self):
        return APP_TYPE

    def get_app_id(self):
        return APP_ID

    def get_node_name(self):
        return NODE_NAME

    def get_nickname(self):
        return NICKNAME

    def get_approbation(self):
        return APPROBATION

    def info_pub(self):
        return ""

    def info_sub(self):
        return ""

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_start()

        # inicializacia SDL2
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
            sys.exit(1)

        # vytvor a zobraz okno
        flags = sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_WINDOW_BORDERLESS
        window = sdl2.SDL_CreateWindow(b"Priklad kreslenia mysou", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, 800, 600, flags)

        # priprav pristup na kreslenie do okna (pozadie okna vyfarbi na bielo)
        renderer = sdl2.SDL_CreateRenderer(window, -1, sdl2.SDL_RENDERER_SOFTWARE)
        sdl2.SDL_SetRenderDrawColor(renderer, 255, 255, 255, 0)                         # nastav farbu kreslenia
        sdl2.SDL_RenderClear(renderer)                                                  # vymaz celu obrazovku danou farbou
        sdl2.SDL_RenderPresent(renderer)                                                # update obrazovky (premietnutie zmien)

        # event loop
        self.running = True
        event = sdl2.SDL_Event()
        while self.running:
            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
                # spracuvaj eventy
                if event.type == sdl2.SDL_MOUSEBUTTONDOWN:  # event: mousebuttondown
                    # nacitaj farbu na pozicii kurzora mysi
                    out = (sdl2.Uint8 * 3)()
                    sdl2.SDL_RenderReadPixels(renderer, sdl2.SDL_Rect(event.motion.x, event.motion.y, 1, 1), sdl2.SDL_PIXELFORMAT_RGB888, out, 3)
                    print(out[0], out[1], out[2])
                if event.type == sdl2.SDL_MOUSEBUTTONUP:    # event: mousebuttonup
                    print(event.button.button)
                if event.type == sdl2.SDL_MOUSEMOTION:      # event: mousemotion
                    sdl2.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 0)                    # nastav farbu kreslenia: r, g, b, a
                    sdl2.SDL_RenderDrawPoint(renderer, event.motion.x, event.motion.y)   # kresli bod na pozicii kurzora mysi
                    sdl2.SDL_RenderPresent(renderer)                                     # update obrazovky (premietnutie zmien)
                if event.type == sdl2.SDL_QUIT:             # event: quit
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
    app = SkelSDL()
    app.start()
    app.run()


