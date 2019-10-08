#!/usr/bin/python3

# PYTHONPATH musi odkazoat na absolutnu cestu k .../chodba-framework/base

# tato aplikacia sa spusta priamo z os (vzdy pri starte os); a to na kazdom uzle

import sys
import socket
import paho.mqtt.client as mqtt
import base_app

APP_NAME = "node_manager"
APP_TYPE = "system"

# na poziadnie oznam typ
if len(sys.argv) == 2 and sys.argv[1]=="type":
    print(APP_TYPE)
    sys.exit(1)

# na poziadnie oznam, kde sa ma spustit: * na vsetkych, ? na lubovolnom, <nazov> na konkretnom
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

    def get_app_type(self):
        return APP_TYPE

    def info_pub(self):
        return ""

    def info_sub(self):
        return "node/" + NODE_NAME

    def on_node_message(self, client, userdata, message):
        sprava = message.payload.decode()
        print("aaaaaaaaaaaaaaa: " + sprava)
        #TODO spusti danu frontend appku. priklad spravy: teplomer_alert a b c => spusti danu appku nasledovne: teplomer_alert NODE_NAME a b c

    def run(self):
        self.client.message_callback_add('node/' + NODE_NAME, self.on_node_message)
        self.client.subscribe("node/" + NODE_NAME)
        # cakaj
        self.client.loop_forever()


if __name__ == '__main__':
    app = NodeManager()
    app.start()
    app.run()


