#!/usr/bin/python3

"""teplomer.py: Zobrazovanie nameranej teploty (z databazy)."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import time
import datetime
import base_app

FONT_PATH = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
FONT_SIZE = 30
FS_ENCODING = "utf-8"

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import sys
import ctypes
import sdl2
import sdl2.sdlimage
import sdl2.sdlttf          # libsdl2-ttf-2.0-0

class Teplomer(base_app.BaseApp):

    def on_msg(self, msg):
        self.status = "kreslim graf"
        resp = msg["resp"]
        cas = []
        teplota = []
        vlhkost = []
        for r in resp:
            cas.append(datetime.datetime.strptime(r["timestamp"], "%Y%m%d%H%M%S%f"))   #.timestamp())
            #cas.append(r["timestamp"])
            teplota.append(r["temperature"])
            vlhkost.append(r["humidity"])

        # vykresli graf
        font = {'family' : 'sans-serif',
                'weight' : 'bold',
                'size'   : 22}
        matplotlib.rc('font', **font)

        fig, axt = plt.subplots(figsize=(20, 11), dpi=96)
        axt.set_title('teplota za poslednych ' + str(self.hist_dni) + ' dni')
        axt.set_xlim(cas[0], cas[-1])

        axt.set_ylabel('teplota', color='tab:red')
        axt.plot(cas, teplota, 'r')
        axt.tick_params(axis='y', labelcolor='tab:red')
        #axt.legend(['teplota'])

        axh = axt.twinx()
        axh.set_ylabel('vlhkost', color='tab:blue')
        axh.plot(cas, vlhkost, 'b')
        axh.tick_params(axis='y', labelcolor='tab:blue')
        #axh.legend(['vlhkost'])

        xax = axt.get_xaxis()
        xax.set_major_formatter(mdates.DateFormatter("%d.%m"))
        dOd = datetime.date(cas[0].year, cas[0].month, cas[0].day)
        dDo = datetime.date(cas[-1].year, cas[-1].month, cas[-1].day)
        xax.set_ticks([dOd + datetime.timedelta(days=x) for x in range((dDo-dOd).days + 1)])
        _=plt.xticks(rotation=45)

        #plt.plot(cas, teplota, 'r', cas, vlhkost, 'b')
        #plt.ylabel('some numbers')

        plt.tight_layout()
        plt.savefig("/tmp/teplota.png")
        self.obrazok = sdl2.sdlimage.IMG_Load(str.encode("/tmp/teplota.png"))

        self.status = "hotovo"


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
        self.window = sdl2.SDL_CreateWindow(b"Teplomer", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, 1024, 768, flags)

        # zisti a zapamataj rozmery vytvoreneho okna
        w, h = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_GetWindowSize(self.window, ctypes.byref(w), ctypes.byref(h))
        self.window_w, self.window_h = w.value, h.value

        # priprav pristup na kreslenie do okna
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_SOFTWARE)
        self.windowsurface = sdl2.SDL_GetWindowSurface(self.window)
        self.font = sdl2.sdlttf.TTF_OpenFont(FONT_PATH.encode("ascii"), FONT_SIZE)

        # poziadaj o data
        self.status = "citam data"
        hist = (datetime.datetime.now() - datetime.timedelta(self.hist_dni)).strftime('%Y%m%d%H%M%S%f')
        #st = datetime.now().strftime('%Y%m%d%H%M%S%f') #TODO
        #hist = datetime.strftime(datetime.now() - timedelta(self.hist_dni), '%Y%m%d%H%M%S%f')
        msg = { "msg": "find", "name": "teplota_vlhkost", "src": self.get_src(), "query": { "timestamp": { "$gt": hist } } }
        #print("posielaaaam", str(msg))          #TODO
        self.client.publish(topic="database", payload=json.dumps(msg), qos=0, retain=False)

        # event loop
        self.running = True
        event = sdl2.SDL_Event()
        while self.running:
            # kresli
            sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 0)
            sdl2.SDL_RenderClear(self.renderer)
            if self.status != "hotovo":
                # vypis spravu
                nazov = sdl2.sdlttf.TTF_RenderUTF8_Blended(self.font, self.status.encode(FS_ENCODING), sdl2.SDL_Color(255, 255, 255))
                r = sdl2.SDL_Rect()
                r.x, r.y = 10, int(self.window_h - nazov.contents.h - 10)
                r.w, r.h = nazov.contents.w, nazov.contents.h
                sdl2.SDL_BlitSurface(nazov, None, self.windowsurface, r)
            else:
                # kresli obrazok
                r = sdl2.SDL_Rect()
                r.x, r.y = 0, 0
                r.w, r.h = self.obrazok.contents.w, self.obrazok.contents.h
                sdl2.SDL_BlitSurface(self.obrazok, None, self.windowsurface, r)
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
    app = Teplomer()
    app.process_args(sys.argv)
    app.start()

