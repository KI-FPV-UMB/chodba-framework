#!/usr/bin/python3

"""teplota_vlhkost.py: v pravidelnom intervale zmeria teplotu a vlhkost a zapise ju do databazy."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# PYTHONPATH musi odkazovat na absolutnu cestu k .../chodba-framework/base

import sys
import os
import paho.mqtt.client as mqtt
import json
import base_app
import time
import Adafruit_DHT
import numpy as np

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
POCET_MERANI = 5

class TeplotaVlhkost(base_app.BaseApp):

    def on_msg(self, msg):
        None

    # vypocitaj smerodajnu odchilku z niekolkych merani a uplne odstran hodnoty, ktore prilis vybocuju (outliers)
    def odstran_sum(self, hodnoty, std_factor = 2):
        # https://forum.dexterindustries.com/t/solved-dht-sensor-occasionally-returning-spurious-values/2939/5
        mean = np.mean(hodnoty)
        standard_deviation = np.std(hodnoty)
        if standard_deviation == 0:
            return hodnoty
        vysledok = [element for element in hodnoty if element > mean - std_factor * standard_deviation]
        vysledok = [element for element in vysledok if element < mean + std_factor * standard_deviation]
        return vysledok

    def run(self):
        # spracovavaj mqtt spravy
        self.client.loop_start()
        # meraj teplotu a vlhkost
        self.running = True
        while self.running:
            # zmeraj vlhkost a teplotu
            humis = []
            temps = []
            for i in range(POCET_MERANI):
                h, t = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
                humis.append(h)
                temps.append(t)
                time.sleep(0.1)
            humidity = np.mean(self.odstran_sum(humis))
            temperature = np.mean(self.odstran_sum(temps))
            # zapis do db
            msg = { "humidity": humidity, "temperature": temperature }
            self.publish_message("insert", msg, "database")
            # cakaj
            time.sleep(self.measurement_pause_s)

    def stop(self):
        # zastav spracovanie mqtt
        super().stop()
        # zastav loop s meranim
        self.running = False


if __name__ == '__main__':
    app = TeplotaVlhkost()
    app.process_args(sys.argv)
    app.start()

