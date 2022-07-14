#!/usr/bin/python3

"""temp_humi.py: in configured interval measure temperature and humidity and send it to storage."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)

import sys
import time
import numpy as np
import Adafruit_DHT

from base import base_app

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
NO_MEASURES = 5

class TempHumi(base_app.BaseApp):

    def remove_noise(self, values, std_factor = 2):
        """calculate standard deviation from a few measurements and remove outliers"""
        # https://forum.dexterindustries.com/t/solved-dht-sensor-occasionally-returning-spurious-values/2939/5
        mean = np.mean(values)
        standard_deviation = np.std(values)
        if standard_deviation == 0:
            return values
        result = [element for element in values if element > mean - std_factor * standard_deviation]
        result = [element for element in result if element < mean + std_factor * standard_deviation]
        return result

    def run(self):
        super().run()
        # start processing of mqtt messages
        self.client.loop_start()
        self.running = True
        while self.running:
            # measure temperature and humidity
            humis = []
            temps = []
            for i in range(NO_MEASURES):
                h, t = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
                humis.append(h)
                temps.append(t)
                time.sleep(0.1)
            humidity = np.mean(self.remove_noise(humis))
            temperature = np.mean(self.remove_noise(temps))
            # send to storage
            msg = { "humidity": humidity, "temperature": temperature }
            self.pub_msg("insert", msg, "storage")
            # wait
            time.sleep(self.measurement_pause_s)

    def stop(self):
        # stop processing mqtt messages
        super().stop()
        # stop measure loop
        self.running = False


if __name__ == '__main__':
    app = TempHumi()
    app.process_args(sys.argv)
    app.start()

