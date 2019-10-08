#!/usr/bin/python3

# PYTHONPATH musi odkazoat na absolutnu cestu k .../chodba-framework/base

# tato aplikacia sa ako jedina spusta priamo z os (vzdy pri starte os); a to na kazdom uzle

import sys
import paho.mqtt.client as mqtt
import socket
import base_app

APP_NAME = "node_manager"

# na poziadnie oznam, kde sa ma spustit: * na vsetkych, ? na lubovolnom, <n> na konkretnom
if len(sys.argv) == 2 and sys.argv[1]=="runon":
    # zobraz informaciu, na ktorych uzloch sa ma backend spustat
    print("*")
    sys.exit(1)

# ako parameter sa ocakava nazov uzla, kde sa backend spusta
NODE_NAME = socket.gethostname()
print("nazov uzla: " + NODE_NAME)

class NodeManager(base_app.BaseApp):

    def get_app_name(self):
        return APP_NAME

    def info_pub(self):
        return ""

    def info_sub(self):
        return "run_frontend/" + NODE_NAME

    def on_run_frontend_message(self, client, userdata, message):
        sprava = message.payload.decode()
        print("aaaaaaaaaaaaaaa: " + sprava)
        #TODO spusti danu frontend appku. priklad spravy: teplomer_alert a b c => spusti danu appku nasledovne: teplomer_alert NODE_NAME a b c

    def run(self):
        self.client.message_callback_add('run_frontend/' + NODE_NAME, self.on_run_frontend_message)
        self.client.subscribe("run_frontend/" + NODE_NAME)
        # cakaj
        app.client.loop_forever()


if __name__ == '__main__':
    app = NodeManager()
    app.start()
    app.run()


