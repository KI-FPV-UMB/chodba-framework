#!/usr/bin/python3

"""gallery.py: Slideshow of images from randomly selected subdirectory."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)

import os
import random
import time
import logging

import sys
import ctypes
import sdl2
import sdl2.sdlimage
import sdl2.sdlttf          # libsdl2-ttf-2.0-0

from base import base_app

SORTED_FILE = "sorted"
NOTITLE_FILE = "notitle"
FONT_PATH = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
#FONT_PATH = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"
#FONT_PATH = "/usr/share/fonts/truetype/ttf-liberation/LiberationSans-Regular.ttf"
FONT_SIZE = 120
FONT_OUTLINE = 3
FS_ENCODING = "utf-8"

class Gallery(base_app.BaseApp):

    def next_image(self):
        #TODO aj z videi => ak sa vyberie video, tak to sa da cele prehrat; ked prehravanie skonci, tak stop
        # read an image
        if self.sorted:
            # in order
            n = self.current
            self.current += 1
            if self.current >= len(self.files):
                self.current = 0
        else:
            # randomly
            n = self.current = random.randint(0, len(self.files)-1)
        logging.info("[" + self.config.name + "]   drawing " + str(n) + ": " + self.files[n])
        if self.image is not None:
            sdl2.SDL_FreeSurface(self.image)
        self.image = sdl2.sdlimage.IMG_Load(str.encode(self.files[n]))

    def draw_image(self):
        #logging.info("[" + self.config.name + "]   kreslim : " + self.files[self.current])
        if self.image is None or self.image.contents is None:
            self.next_image()
        # clear background
        sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 0)
        sdl2.SDL_RenderClear(self.renderer)
        # calculate scale
        aw = self.image.contents.w / self.window_w
        ah = self.image.contents.h / self.window_h
        r = sdl2.SDL_Rect()
        a = max(aw, ah)
        nw, nh = self.image.contents.w / a, self.image.contents.h / a
        r.x, r.y = int(self.window_w/2 - nw/2), int(self.window_h/2 - nh/2)
        r.w, r.h = int(nw), int(nh)
        # draw
        sdl2.SDL_BlitScaled(self.image, None, self.windowsurface, r)
        #sdl2.SDL_UpdateWindowSurface(self.window)

        # display name of directory
        if not self.notitle:
            # draw with black color outlined text
            nazov_outlined = sdl2.sdlttf.TTF_RenderUTF8_Blended(self.font_outlined, self.folder.encode(FS_ENCODING), sdl2.SDL_Color(0, 0, 0))
            r = sdl2.SDL_Rect()
            r.x, r.y = int(self.window_w/2 - nazov_outlined.contents.w / 2), int(self.window_h - nazov_outlined.contents.h - 10)
            r.w, r.h = nazov_outlined.contents.w, nazov_outlined.contents.h
            sdl2.SDL_BlitSurface(nazov_outlined, None, self.windowsurface, r)
            # draw smaller text with white color
            nazov = sdl2.sdlttf.TTF_RenderUTF8_Blended(self.font, self.folder.encode(FS_ENCODING), sdl2.SDL_Color(255, 255, 255))
            r = sdl2.SDL_Rect()
            r.x, r.y = int(self.window_w/2 - nazov.contents.w / 2 + FONT_OUTLINE / 2), int(self.window_h - nazov.contents.h - 10 + FONT_OUTLINE / 2)
            r.w, r.h = nazov.contents.w, nazov.contents.h
            sdl2.SDL_BlitSurface(nazov, None, self.windowsurface, r)

        # display changes
        sdl2.SDL_RenderPresent(self.renderer)
        #sdl2.SDL_FreeSurface(self.image)             # TODO s tymto to pada
        #sdl2.SDL_FreeSurface(nazov)

    def run(self):
        # choose random directory with images
        subdirs = [d for d in os.listdir(".") if os.path.isdir(d)]
        #subdirs = [x[0] for x in os.walk(".")]
        if len(subdirs) <= 1:
            log = { "log": "gallery contains none subdirectory with images!" }
            self.pub_msg("log", log, "app_controller" )
            return
        d = random.choice(subdirs)
        # d = subdirs[4]
        logging.info("[" + self.config.name + "] selecting " + d)
        self.folder = d
        self.files = [os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)) and (f.endswith(".png") or f.endswith(".jpg") or f.endswith(".mp4"))]
        # self.files = [os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)) and (f.endswith(".mp4"))]
        ssorted = os.path.join(d, SORTED_FILE)
        self.sorted = os.path.isfile(ssorted)
        if self.sorted and ssorted in self.files:
            self.files.remove(ssorted)
            self.files.sort()
        self.current = 0                # currently shown image (used when displaying images in order)
        snotitle = os.path.join(d, NOTITLE_FILE)
        self.notitle = os.path.isfile(snotitle)
        if self.notitle and snotitle in self.files:
            self.files.remove(snotitle)

        # initialize SDL2
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
            sys.exit(1)

        if not sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_JPG | sdl2.sdlimage.IMG_INIT_PNG):
            sys.exit(1)

        if sdl2.sdlttf.TTF_Init() <0:
            sys.exit(1)

        # create and show window (full screen)
        flags = sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_WINDOW_BORDERLESS
        self.window = sdl2.SDL_CreateWindow(b"Galeria", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, 1024, 768, flags)

        # save size of the window
        w, h = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_GetWindowSize(self.window, ctypes.byref(w), ctypes.byref(h))
        if self.args.screen_width is not None and self.args.screen_height is not None:
            self.window_w, self.window_h = self.args.screen_width, self.args.screen_height
        else:
            self.window_w, self.window_h = w.value, h.value

        # prepare window renderer
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_SOFTWARE)
        self.windowsurface = sdl2.SDL_GetWindowSurface(self.window)
        self.font = sdl2.sdlttf.TTF_OpenFont(FONT_PATH.encode("ascii"), FONT_SIZE)
        sdl2.sdlttf.TTF_SetFontOutline(self.font, 0); 
        self.font_outlined = sdl2.sdlttf.TTF_OpenFont(FONT_PATH.encode("ascii"), FONT_SIZE)
        sdl2.sdlttf.TTF_SetFontOutline(self.font_outlined, FONT_OUTLINE); 

        # clear window
        sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 0)
        sdl2.SDL_RenderClear(self.renderer)

        # start processing of mqtt messages
        super().run()

        # event loop
        self.image = None
        last_draw = time.time()
        self.running = True
        event = sdl2.SDL_Event()
        while self.running:
            self.draw_image()
            if time.time() - last_draw > self.config.delay_s:
                self.next_image()
                last_draw = time.time()
                # TODO cas pauzy postupne skracovat

            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
                # spracuvaj eventy
                if event.type == sdl2.SDL_QUIT:             # event: quit
                    self.running = False
                    break
            sdl2.SDL_Delay(500)                             # in ms

        # release resources
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

    def stop(self):
        # stop processing mqtt
        super().stop()
        # stop processing SDL events
        self.running = False


if __name__ == '__main__':
    app = Gallery()
    app.process_args(sys.argv)
    app.start()

