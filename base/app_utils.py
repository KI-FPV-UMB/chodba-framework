#!/usr/bin/python3

"""app_utils.py: pomocne programy"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"


class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class ControlElement:
    def __init__(self, name, x, y, w, h, title, typ):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.type = typ          # button/button_submit/input_text/input_number/kreslenie


