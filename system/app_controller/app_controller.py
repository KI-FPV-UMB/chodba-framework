#!/usr/bin/python3

"""app_controller.py: handles lifecycle of applications. This application is run directly from OS (using systemd). There can be only one instance in the network (on a main node). Must be executed as first application."""
__author__ = "Michal Vagac"
__email__ = "michal.vagac@gmail.com"

# set PYTHONPATH to project root (chodba-framework)

import sys
import os
import json
import random
import time
import logging
import threading
from base import base_app
from base import app_utils

# timeout (in seconds) after which can be user executed application replaced by another one
USER_TIMEOUT = 45

# frequency of pinging status of applications. The applications with timestamp older than current_time-TIMESTAMP_CHECK
# are asked for their status. The applications with timestamp older than current_time-3*TIMESTAMP_CHECK are removed from
# the list of running applications (it is supposed they are not running anymore)
TIMESTAMP_CHECK = 60

SYSTEM_APPS_PATH = "../../system/"
APPS_PATH = "../../apps/"

class App:
    """Class storing necessary information about running application"""
    def __init__(self):
        self.name = None
        self.type = None
        self.id = None
        self.node = None
        self.status = None
        self.config = {}
    def __str__(self):
        ret = ""
        if self.name is not None:
            ret += ", " + self.name
        if self.type is not None:
            ret += ", " + self.type
        if self.node is not None:
            ret += ", " + self.node
        if self.status is not None:
            ret += ", " + self.status
        if len(ret) > 0:
            ret = ret[2:]
        return "(" + ret + ")"
    __repr__ = __str__

class AppController(base_app.BaseApp):

    def __init__(self):
        super(AppController, self).__init__()
        self.running_apps = []
        self.quitting = False

    def list_offline_apps(self, type: str, labels: list, as_json: bool) -> list:
        """Build list of all available (offline) and enabled applications.
        If labels is specified, only applications with specified labels are returned."""
        ret = []
        for entry in os.listdir(APPS_PATH):
            if os.path.isdir(os.path.join(APPS_PATH, entry)):
                app = App()
                # read application's configuration
                app_config = self.read_config(os.path.join(APPS_PATH, entry))
                if app_config is None:
                    logging.warning("[" + self.config.name + "] skipping " + entry)
                    continue
                has_labels = False
                for k in app_config.keys():
                    setattr(app, k, app_config[k])
                    if k == "labels":
                        has_labels = True
                if type is not None and app.type != type:
                    continue
                if app.enabled and (labels is None or (has_labels and (set(labels) & set(app.labels)))):
                    # the application is enabled and has corresponding labels (if required)
                    if as_json:
                        ret.append(app.__dict__)       # return as dictionary -> to enable json serialization
                    else:
                        ret.append(app)
        return ret

    def is_app_running(self, name: str, node=None) -> bool:
        """Test if specified application is running."""
        for app in self.running_apps:
            if app.name == name and (node == None or node == app.node):
                return True
        return False

    def start_app(self, app: App):
        """Send a message to node_manager to run selected application on specified node"""
        logging.info("[" + self.config.name + "] starting " + app.name + " on " + app.node)
        self.pub_msg("start", { "type": app.type, "name": app.name }, "node/" + app.node)

    def stop_app(self, app: App) -> None:
        """Stop specified application. The application is removed from list of applications only after message confirming
        stopping is retrieved."""
        topic = super().get_specific_topic(app.name, app.node)[0]
        self.pub_msg("stop", {}, topic)

    def start_all_backends(self, node_managers: list):
        """Run all backend applications according to their runon configuration."""
        # iterate over list of all backend applications
        apps_list = self.list_offline_apps(app_utils.APP_TYPE_BACKEND, None, False)
        for app in apps_list:
            try:
                if app.runon == "*":
                    # start on each node
                    for node in node_managers:
                        if not self.is_app_running(app.name, node):
                            app.node = node
                            self.start_app(app)
                        else:
                            logging.warning("[" + self.config.name + "] app " + app.name + " is already running on node " + node + "!")
                elif app.runon == "?":
                    # run on one (random node). only if it is not running anywhere yet
                    for nmapp in self.running_apps:
                        if nmapp.name == app.name:
                            logging.warning("[" + self.config.name + "] app " + app.name + " is already running! (on node " + nmapp.node + ")")
                            return
                    node = node_managers[random.randint(0, len(node_managers)-1)]
                    app.node = node
                    self.start_app(app)
                else:
                    # run on specified node
                    if not self.is_app_running(app.name, app.runon):
                        app.node = app.runon
                        self.start_app(app)
                    else:
                        logging.warning("[" + self.config.name + "] app " + app.name + " is already running on node " + app.runon + "!")
            except Exception as e:
                logging.exception("[" + self.config.name + "] error starting " + app.name)

    def start_random_frontend_app(self, node: str):
        """Choose a random application and run it. Only frontend applications with label 'demo' and config demo_time > 0 are considered."""
        # build a list of candidate applications
        apps_list = self.list_offline_apps(app_utils.APP_TYPE_FRONTEND, ["demo"], False)
        candidates = []
        for app in apps_list:
            if app.demo_time > 0:
                candidates.append(app)
        if len(candidates) == 0:
            logging.warning("[" + self.config.name + "] no demo applications was found, there is nothing to run on node " + node)
            return
        # randomly choose one application and run it
        app = candidates[random.randint(0, len(candidates)-1)]
        app.node = node         # since it is loaded from offline apps, it has no node set
        self.start_app(app)

    def update_app_lifecycle_status(self, msg: dict) -> App:
        """Update status (and all properties) of application instance."""
        # find app in the list
        app = None
        for a in self.running_apps:
            if a.name == msg["header"]["name"] and a.node == msg["header"]["node"]:
                app = a
                break

        # if new app, create new instance
        if app is None:
            app = App()
            app.id = msg["header"]["id"]
            app.status = None
            app.name = msg["header"]["name"]
            app.config = self.read_config(os.path.join(APPS_PATH, app.name))

        # update all fields
        prevstat = app.status
        for k in msg["header"].keys():
            setattr(app, k, msg["header"][k])
        app.timestamp = time.time()
        app.status = msg["body"][app_utils.LIFECYCLE_STATUS]

        # add app to list of running apps
        if app not in self.running_apps:
            self.running_apps.append(app)

        return prevstat, app

    def log_apps_status(self, title, apps):
        logging.info("[" + self.config.name + "] " + title)  # + str(self.running_apps))
        apps_sys = []
        apps_back = []
        apps_frnt = []
        # apps_list =
        for app in apps:
            if app.type == app_utils.APP_TYPE_SYSTEM:
                apps_sys.append(app)
            elif app.type == app_utils.APP_TYPE_BACKEND:
                apps_back.append(app)
            elif app.type == app_utils.APP_TYPE_FRONTEND:
                apps_frnt.append(app)
        apps_sys.sort(key=lambda x: x.name)
        apps_back.sort(key=lambda x: x.name)
        apps_frnt.sort(key=lambda x: x.name)

        def log_status(l):
            for app in l:
                if app.node is not None and app.status is not None:
                    logging.info("  " + "{:<20} {:<10} {:<12} {:<15}".format(app.name, app.type, app.node, app.status))
                else:
                    logging.info("  " + "{:<20} {:<10}".format(app.name, app.type))

        log_status(apps_sys)
        log_status(apps_back)
        log_status(apps_frnt)

    def get_specific_topic(self, name: str, node: str) -> list:
        return [app_utils.APP_CONTROLLER_TOPIC]

    def on_app_msg(self, msg):
        """basic method for retrieving messages"""
        msg_type = msg["header"][app_utils.MSG_TYPE]

        if msg_type == app_utils.MSG_TYPE_LIFECYCLE:
            # update and process lifecycle of application
            prevstat, app = self.update_app_lifecycle_status(msg)
            # process starting of node_manager
            if prevstat == "starting" and app.status == "running":
                if app.name == "node_manager":
                    logging.info("[" + self.config.name + "] node_manager started on " + app.node)
                    self.start_all_backends([app.node])
                    self.start_random_frontend_app(app.node)
                elif "demo_time" in app.config:
                    # since it is demo, schedule stopping of the application (only now, after it is already running)
                    t = threading.Timer(int(app.config["demo_time"]), self.stop_app, [app])
                    t.start()

            # process stopping of any application
            if app.status == "stopping":
                self.running_apps.remove(app)
                if not self.quitting and app.type == app_utils.APP_TYPE_FRONTEND:
                    self.start_random_frontend_app(app.node)

        elif msg_type == "log":
            text = "[" + msg["header"]["node"] + "." + msg["header"]["name"] + "] " + msg["body"]["log"]
            if "level" in msg["body"]:
                lvl = msg["body"]["level"]
                if lvl == "error":
                    logging.error(text)
                elif lvl == "warning":
                    logging.warning(text)
                else:
                    logging.info(text)
            else:
                logging.info(text)

        elif msg_type == "stat":
            # log current status
            self.log_apps_status("running apps:", self.running_apps)

        elif msg_type == "start_backends":
            # start required backends on particular nodes
            node_managers = []
            for app in self.running_apps:
                if app.name == "node_manager":
                    node_managers.append(app.node)
            self.start_all_backends(node_managers)

        elif msg_type == "stop_all":
            # stop all applications
            self.quitting = True
            for app in self.running_apps:
                if app.name == self.config.name:
                    continue
                topic = super().get_specific_topic(app.name, app.node)[0]
                logging.info("[" + self.config.name + "] stopping " + topic)
                self.pub_msg("stop", {}, topic)

        elif msg_type == "applications":
            # state: all|running
            # type: system|backend|frontend
            # labels: ...
            apps_list = []
            if not "state" in msg.body or msg.body.state == "all":
                if not "type" in msg.body or msg.body.type == app_utils.APP_TYPE_SYSTEM:
                    apps_list += self.list_offline_apps(SYSTEM_APPS_PATH, msg.get("labels", None), True)
                if not "type" in msg.body or msg.body.type == app_utils.APP_TYPE_BACKEND:
                    apps_list += self.list_offline_apps(app_utils.APP_TYPE_BACKEND, msg.get("labels", None), True)
                if not "type" in msg.body or msg.body.type == app_utils.APP_TYPE_FRONTEND:
                    apps_list += self.list_offline_apps(app_utils.APP_TYPE_FRONTEND, msg.get("labels", None), True)
            elif msg.state == "running":
                for app in self.running_apps:
                    if not "type" in msg.body or msg.body.type == app.type:
                        apps_list.append(app.__dict__)
            resp = { "applications": apps_list }
            topic = super().get_specific_topic(msg.header.name, msg.header.node)[0]
            logging.debug(json.dumps(resp), topic)         #TODO
            self.pub_msg("applications", resp, topic)

        elif msg_type == "workspaces":
            wrkspcs_list = []
            """
            TODO moved to configuration file
            WORKSPACES_LAYOUT = dict([("mvagac-X230", app_utils.Rect(0, 0, 1, 1)), ])
            for app in self.running_apps:
                if app.name == "node_manager":
                    if app.node in WORKSPACES_LAYOUT.keys():
                        WORKSPACES_LAYOUT[app.node].active = True
            for k in WORKSPACES_LAYOUT.keys():
                WORKSPACES_LAYOUT[k].name = k
                wrkspcs_list.append(WORKSPACES_LAYOUT[k].__dict__)
            """
            resp = { "grid_width": "4", "grid_height": "2", "workspaces": wrkspcs_list }
            topic = super().get_specific_topic(msg.header.name, msg.header.node)[0]
            logging.debug(json.dumps(resp), topic)         #TODO
            self.pub_msg("workspaces", resp, topic)

        elif msg_type == "approbations":
            apprs_list = [ "AI1", "AI2", "UIN1", "UIN2" ]
            resp = { "approbations": apprs_list }
            topic = super().get_specific_topic(msg.header.name, msg.header.node)[0]
            logging.debug(json.dumps(resp), topic)         #TODO
            self.pub_msg("approbations", resp, topic)

        else:
            super().on_app_msg(msg)

    def check_inactive_users(self):
        #TODO
        last_timestamp_check = time.time()
        while True:
            time.sleep(5)
            # prejdi aplikacie a pri user aplikaciach kontroluj cas poslednej aktivity
            for app in self.running_apps:
                if getattr(app, "nickname", None) is not None and getattr(app, "approbation", None) is not None:
                    # user aplikacia, skontroluj cas poslednej aktivity
                    if time.time() - app.timestamp > USER_TIMEOUT:
                        logging.info("[" + self.config.name + "] timeout user app " + app.name)
                        self.stop_app(app)
            # v ovela dlhsom intervale pingni vsetky aplikacie, ktore sa davno neozvali (neupdatli lifecycle)
            if time.time() - last_timestamp_check > TIMESTAMP_CHECK:
                last_timestamp_check = time.time()
                for app in self.running_apps:
                    if last_timestamp_check - app.timestamp > 3*TIMESTAMP_CHECK and app.status == "refreshing":
                        # prilis dlho sa neozvali, asi uz nebezia. odstran ich zo zoznamu
                        logging.info("[" + self.config.name + "] odstranovanie neodpovedajucej app " + app.name)
                        self.running_apps.remove(app)
                        # ak tam nic nebezi, tak tam automaticky spusti novu nahodnu appku
                        if not self.quitting and not app.replaced:
                            obsadeny = False
                            for app2 in self.running_apps:
                                if app2.type == app_utils.APP_TYPE_FRONTEND and app2.node == app.node:
                                    obsadeny = True
                                    break
                            if not obsadeny:
                                self.start_random_frontend_app(app.node)
                    elif last_timestamp_check - app.timestamp > TIMESTAMP_CHECK:
                        # daj im este sancu - posli poziadavku na refresh
                        logging.info("[" + self.config.name + "] refresh stavu " + app.name + " na " + app.node)
                        app.status = "refreshing"
                        topic = super().get_specific_topic(app.name, app.node)[0]
                        self.pub_msg(app_utils.LIFECYCLE_STATUS, {}, topic)

    def run(self):
        super().run()

        # create scheduler for checking inactive user applications
        """t = threading.Thread(target=self.check_inactive_users)
        t.daemon = True
        t.start()"""        #TODO

        self.log_apps_status("all available apps:", self.list_offline_apps(None, None, False))

        # start processing of mqtt messages
        self.client.loop_forever()


if __name__ == '__main__':
    app = AppController()
    app.process_args(sys.argv)
    app.start()

