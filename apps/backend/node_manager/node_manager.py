#!/usr/bin/python3

# PYTHONPATH musi odkazoat na absolutnu cestu k .../chodba-framework/base

import sys
import paho.mqtt.client as mqtt
import base_app

APP_NAME = "frontend_runner"

# na poziadnie oznam, kde sa ma spustit: * na vsetkych, ? na lubovolnom, <n> na konkretnom
if len(sys.argv) == 2 and sys.argv[1]=="run":
    print("*")
    sys.exit(1)

NODE_NO = sys.argv[1]

class FrontendRunner(base_app.BaseApp):

    def get_app_name(self):
        return APP_NAME

    def info(self):
        return "subscriber: run_frontend/" + NODE_NO

    def on_run_frontend_message(self, client, userdata, message):
        sprava = message.payload.decode()
        print("aaaaaaaaaaaaaaa: " + sprava)
        #TODO spusti danu frontend appku. priklad spravy: teplomer_alert a b c => spusti danu appku nasledovne: teplomer_alert NODE_NO a b c

    def run(self):
        self.client.message_callback_add('run_frontend/' + NODE_NO, self.on_run_frontend_message)
        self.client.subscribe("run_frontend/" + NODE_NO)
        # cakaj
        app.client.loop_forever()


if __name__ == '__main__':
    app = FrontendRunner()
    app.start()
    app.run()


