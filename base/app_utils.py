#!/usr/bin/python3

"""app_utils.py: pomocne programy"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

import os
import subprocess

def run_app(path, name, arg=None):
    p = os.path.join(path, name)
    # test pre python app
    f = os.path.join(p, name) + ".py"
    if os.path.isfile(f):
        if arg is None:
            # spusti na pozadi
            subprocess.Popen(["/usr/bin/python3", f])
            return None
        else:
            # spusti a vrat vystup
            result = subprocess.run([f, arg], stdout=subprocess.PIPE)
            return result.stdout.decode('utf-8').strip('\n')
    # test pre java app
    #TODO
    raise Exception('aplikacia nebola najdena alebo neznamy typ aplikacie!')


