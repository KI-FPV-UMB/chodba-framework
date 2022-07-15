#!/usr/bin/python3

"""hw_monitor.py: monitor hardware status of current system; send result to storage"""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)

import sys
import time
import subprocess

from base import base_app

class HwMonitor(base_app.BaseApp):

    def read_cpu(self):
        proc = subprocess.Popen(['uptime'], stdout=subprocess.PIPE)
        line = proc.stdout.readline().decode('utf-8')
        if not line:
            return
        m = line.split()

        idx = None
        for i in range(len(m)):
            if m[i] == "average:":
                idx = i
                break
        load1 = m[idx+1][:-1] if m[idx+1].endswith(',') else m[idx+1]
        load5 = m[idx+2][:-1] if m[idx+2].endswith(',') else m[idx+2]
        load15 = m[idx+3][:-1] if m[idx+3].endswith(',') else m[idx+3]
        return {"load1": float(load1), "load5": float(load5), "load15": float(load15)}

    def read_memory(self):
        proc = subprocess.Popen(['free'], stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline().decode('utf-8')
            if not line:
                break
            if line.startswith("Mem:"):
                m = line.split()
                return {"total": m[1], "used": m[2], "free": m[3]}

    def read_disks(self):
        proc = subprocess.Popen(['df'], stdout=subprocess.PIPE)
        ret = {}
        while True:
            line = proc.stdout.readline().decode('utf-8')
            if not line:
                break
            if line.startswith("/dev/"):
                m = line.split()
                ret[m[5]] = {"total": m[1], "used": m[2], "free": m[3], "dev": m[0]}
        return ret

    def run(self):
        super().run()
        # start processing of mqtt messages
        self.client.loop_start()
        self.running = True
        while self.running:
            msg = { "node": self.node }
            # gather hw information
            msg["cpu"] = self.read_cpu()
            msg["memory"] = self.read_memory()
            msg["disks"] = self.read_disks()
            # send to storage
            self.pub_msg("insert", msg, "storage")
            # wait
            time.sleep(self.config.measurement_pause_s)

    def stop(self):
        # stop processing mqtt messages
        super().stop()
        # stop measure loop
        self.running = False


if __name__ == '__main__':
    app = HwMonitor()
    app.process_args(sys.argv)
    app.start()

