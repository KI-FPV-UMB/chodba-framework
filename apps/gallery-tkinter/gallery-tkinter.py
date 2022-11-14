#!/usr/bin/python3

"""gallery-tkinter.py: Slideshow of images from randomly selected subdirectory."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)

import os
import random
import time
import logging
import sys
import threading

from PIL import Image, ImageTk
import tkinter
import tkinter.messagebox

from base import base_app

SORTED_FILE = "sorted"
NOTITLE_FILE = "notitle"

# class HandleContent(threading.Thread):
#     def __init__(self, app):
#         super().__init__()
#         self.app = app
#
#     def run(self):
#         time.sleep(3)
#         self.app.change_image()
        # self.app.canvas.itemconfig(self.app.img_container, image=self.app.img2)


class Gallery(base_app.BaseApp):

    def next_image(self):
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

    def get_image(self):
        # open as PIL image
        img = Image.open(str.encode(self.files[self.current]))
        # resize to window size
        imgWidth, imgHeight = img.size      # img.width(), img.height()
        ratio = min(self.w / imgWidth, self.h / imgHeight)
        img = img.resize((int(imgWidth*ratio), int(imgHeight*ratio)), Image.Resampling.LANCZOS)
        # return as Tkinter image
        return ImageTk.PhotoImage(img)

    def change_image(self):
        self.next_image()
        img = self.get_image()
        self.canvas.itemconfig(self.img_container, image=img)

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

        # show window
        self.top = tkinter.Tk()
        self.top.wm_attributes("-type", "splash")       # no decorations
        self.top.wm_attributes("-fullscreen", True)
        self.top.configure(background="#000")
        self.w, self.h = self.top.winfo_screenwidth()-3, self.top.winfo_screenheight()-3
        if self.args.screen_width is not None and self.args.screen_height is not None:
            self.w, self.h = self.args.screen_width-3, self.args.screen_height-3
        self.top.geometry("{0}x{1}+0+0".format(self.w, self.h))
        self.top.focus_set()
#        self.top.resizable(False, False)
#        self.top.update_idletasks()
#        self.top.overrideredirect(True)

        # window content
        # self.canvas = tkinter.Canvas(self.top, width=self.w, height=self.h, bg="#000", highlightthickness=0)
        # self.canvas.pack()

        img = self.get_image()
        self.label = tkinter.Label(self.top, image=img)
        self.label.pack()
        # self.img_container = self.canvas.create_image(0, 0, anchor=tkinter.NW, image=img)

        # self.top.after(1000, self.change_image)
        # thread1 = threading.Thread(target=self.change_image)
        # thread1.start()

        # hc = HandleContent(self)
        # hc.start()

        # start processing of mqtt messages
        super().run()

        # work
        # self.top.mainloop()
        self.running = True
        last_draw = time.time()
        while self.running:
            self.top.update()

            if time.time() - last_draw > self.config.delay_s:
                # self.change_image()
                self.next_image()
                img = self.get_image()
                self.label.configure(image=img)
                self.label.image = img
                last_draw = time.time()

            time.sleep(1)

        self.top.withdraw()

    def stop(self):
        # stop processing mqtt
        super().stop()
        # close window
        self.running = False
        # self.top.after(0, self.top.destroy)

if __name__ == '__main__':
    app = Gallery()
    app.process_args(sys.argv)
    app.start()

