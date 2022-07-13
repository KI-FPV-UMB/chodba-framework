#!/usr/bin/python3

"""app_utils.py: helper programs"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

APP_CONTROLLER_TOPIC = "app_controller"
MSG_TYPE = "msg"
MSG_TYPE_LIFECYCLE = "lifecycle"
LIFECYCLE_STATUS = "status"

APP_TYPE_SYSTEM = "system"
APP_TYPE_BACKEND = "backend"
APP_TYPE_FRONTEND = "frontend"

class Rect:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class ControlElement:
    def __init__(self, name: str, x: int, y: int, w: int, h: int, title: str, typ: str):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.type = typ          # button/button_submit/input_text/input_number/drawing


