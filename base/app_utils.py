#!/usr/bin/python3

"""app_utils.py: pomocne programy"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

import os
import sys
import subprocess
import socket
import json
import random


def process_args(args):
    nickname = None
    approbation = None
    user_topic = None

    if len(args) > 2:
        nickname = args[1]
        approbation = args[2]

    if len(args) > 3:
        user_topic = args[3]

    return nickname, approbation, user_topic


def run_app(path, name, arg1=None, arg2=None, arg3=None):
    p = os.path.join(path, name)
    # test pre python app
    f = os.path.join(p, name) + ".py"
    if os.path.isfile(f):
        if arg1 is None:
            # ak je bez parametrov, spusti na pozadi
            subprocess.Popen(["/usr/bin/python3", name + ".py"], cwd=p)
            return None
        elif arg1 is not None and arg2 is None:
            # ak je prave 1 parameter, spusti a vrat vystup
            result = subprocess.run([f, arg1], stdout=subprocess.PIPE)
            return result.stdout.decode("utf-8").strip("\n")
        elif arg1 is not None and arg2 is not None and arg3 is None:
            # ak su 2 parametre, spusti na pozadi
            subprocess.Popen(["/usr/bin/python3", name + ".py", arg1, arg2], cwd=p)
            return None
        else:
            # ak su 3 parametre, spusti na pozadi
            subprocess.Popen(["/usr/bin/python3", name + ".py", arg1, arg2, arg3], cwd=p)
            return None
    # test pre java app
    #TODO
    raise Exception("aplikacia nebola najdena alebo neznamy typ aplikacie!")

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
        self.typ = typ          # button/button_submit/input_text/input_number/kreslenie


