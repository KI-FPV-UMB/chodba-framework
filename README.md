# chodba-framework

Simple framework for managing distributed applications used (mostly) to display information.
In our case, we use it in the department corridors to show course timetable, news,
interesting/funny quotes, bus timetable, etc.

Set PYTHONPATH to location of chodba-framework/base/

# Main framework elements

The system consists of **applications**, communicating via MQTT protocol
(sending and receiving **messages**).

## Applications

Each application extends BaseApp Python class. This class initializes logging
and loads application config file.

The running application has following two attributes:
  * _id_ - randomly generated hash
  * _node_ - name of node (computer) the application is running on (automatically set to hostname)

Further, it provides methods for handling messages and starting and stopping the application:
  * _pub_msg(msg_type, msg_body, topic)_ - basic method for sending messages
  * _pub_lifecycle(status)_ - helper method for sending lifecycle status
  * _on_msg_ - method for handling all application messages. Several specific messages (quit, info, status) are handled immediately. For all other (unknown) messages the method *on_app_msg* is called.
  * _on_app_msg_ - method for handling specific application messages (extended by offspring class)
  * _start_ - initializes mqtt client and connects to configured MQTT broker. Immediately it sends lifecycle message 'starting'. Then it subscribes to ```node/<node_name>/<app_name>``` topics. After initialization, it sends lifecycle message 'running'.
  * _run_ - method with implementation of application business logic. This (parent's) method should be invoked after start completion.
  * _stop_ - Sends lifecycle message 'stopping' and disconnects from MQTT broker.

Each application reacts to following message types:
  * _stop_ - stops the application (and send information about stopping)
  * _lifecycle_ - publish current lifecycle (default always send 'running' state)
  * _debug_ - turn debugging on/off

If message type is other than any of the listed types, processing is moved to _on_app_msg_ method.

Each application needs minimal configuration containing:
  * _name_ - application name
  * _type_ - one of: system / backend / frontend

Besides that there are several optional configuration properties, such as:
  * _enabled_ - only enabled applications can be run
  * _runon_ - if specified, the application can be invoked only on here specified node
  * _labels_ - list of labels (e.g. app, demo, fun, ...)
  * _demo_time_ - how long will application run

Example of main system application configuration:
```json
{
  "name": "demo",
  "type": "frontend",
  "enabled": true,
  "runon": "chodba-ki01"
}
```

When starting the application, several command line arguments are expected:
  * _broker_host_ - e.g. localhost
  * _broker_port_ - e.g. 1883
  * _broker_transport_ - e.g. tcp
  * _screen_width_ or -
  * _screen_height_ or -
  * _[user_topic]_ - optional argument used when application is invoked manually by user
  * _[nickname]_ - nickname of user who invoked the application (if any)
  * _[approbation]_ - study approbation of user who invoked the application (if any)

## Messages

Each message must contain header and body parts. The header contains following attributes:
  * _msg_ - type of message
  * _timestamp_ - datetime of creation of the message
  * _id_ - generated id of source application
  * _name_ - name of source application
  * _type_ - type of source application
  * _node_ - node source application runs on

Example of a lifecycle message:
```json
{
  "header": {
    "msg": "lifecycle",
    "timestamp": "",
    "id": "",
    "name": "demo",
    "type": "frontend",
    "node": "chodba-ki01"
  },
  "body": {
    "status": "running"
  }
}
```

## Topics

Each application listens on topic ```node/<node>/<name>```. AppController listens on topic ```app_controller```.

# Basic application types

Three types of applications are supported:
  * system - supporting applications (AppController and NodeManager)
  * frontend - applications displayed on monitor
  * backend - applications running in background

## AppController

Main task of the AppController application is controlling (starting and stopping)
other applications running on different nodes. It maintains a list of running applications
and periodically checks status of the applications.

There must be only one instance in the environment (managed nodes). The instance must be
started from OS (for example using systemd).

After starting up, AppController binds to a ```app_controller``` topic. In current version it
responds to following message types:
  * _lifecycle_ - updates lifecycle status for running applications
  * _start_backends_ - starts all backends applications. This action is invoked once upon overall system startup. Backend applications are invoked according to its runon configuration parameter.
  * _stop_all_ - stops all running applications (both backend and frontend)
  * _applications_ - returns required list of applications. Supported arguments are: state (all|running), type (system|backend|frontend), labels (list)
  * _workspaces_ - returns list of all workspaces
  * _approbations_ - returns list of all known approbations

All the responses are asynchronously sent to topic of requiring application.

After stopping frontend application on a node, new random frontend demo application
(with label 'demo') is chosen and started. A demo application is automatically stopped
after specified amount (demo_time) of time and replaced with another demo application.

Example message used to start application. The message is sent to node_manager (i.e. to topic ```node/<node>```)
 ```json
{
  "header": {
    "msg": "start",
    ...
  },
  "body": {
    "type": "frontend",
    "name": "demo"
  }
}
```
Example message used to stop application. The message is sent directly to the application (i.e. to topic ```node/<node>/<name>```):
```json
{
  "header": {
    "msg": "stop",
    ...
  }
}
```

## NodeManager

NodeManager is second (and last) system application. It's purpose is starting applications
on nodes. Each node (controlled computer) should run one NodeManager application. 

There must be one instance on each managed node (computer). The instance must be
started from OS (for example using systemd).

After starting up, NodeManager binds to a ```node/<node>``` topic. In current version it
responds to following message types:
  * _start_ - starts specified application (invokes os process)
  * _screen_size_ - updates screen size of the node






## Ako na to

Aby mohol byť Váš program spustený v tomto prostredí, musí spĺňať niekoľko podmienok.

1. posiela informacie o zivotnom cykle na topic "master":
   * "msg": "lifecycle"
   * "name": nazov aplikacie (malymi pismenami, bez medzier, diakritiky)
   * "type": "app" alebo "game"
   * "id": unikatny identifikator (pocas jedneho behu aplikacie sa nesmie zmenit!)
   * "node": hostname pocitaca, kde je spustena
   * "status" - stav, co sa s aplikaciou deje:
     * "starting" - pri spustani
     * "ok" - po spusteni
     * "quitting" - pri vypinani

priklad:
```json
{"node": "mvagac-X230", "name": "priklad", "type": "app", "msg": "lifecycle", "id": "70e0c7db6a2834b141b26b80a39b9b", "status": "starting"}
```
2. pocuva topic "app/<svoj_nazov>"; prichodzia sprava ma vzdy "msg":
   * "quit": prikaz na ukoncenie aplikacie
   * "info": na topic "master" posle informacie o sebe:
     * "msg": "info"
     * "name": nazov aplikacie (malymi pismenami, bez medzier, diakritiky)
     * "type": "app" alebo "game"
     * "id": unikatny identifikator (pocas jedneho behu aplikacie sa nesmie zmenit!)
     * "pub": info o topicoch, na ktore posiela spravy (publish)
     * "sub": info o topicoch, na ktorych pocuva (subscribe)

priklad:
```json
{"msg": "info", "pub": "", "sub": "abc", "type": "app", "name": "priklad", "id": "e4d3b84da554c5529d4c469cde86406"}
```
   * "status": na topic "master" posle, ze je ok (atributy ako pri zivotnom cykle):

priklad:
```json
{"msg": "lifecycle", "name": "priklad", "type": "app", "id": "399548a2b577edcad81a7e0a092f092", "status": "ok", "node": "mvagac-X230"}
```

3. pocuva topic "app/<svoj_nazov>/<hostname>"; moze byt rovnaky kod ako pri "app/<svoj_nazov>"

## Prehľad štruktúry MQTT topicov

* master - spravy pre master uzol (aplikaciu)
  * msg=lifecycle => udrziava zoznam beziacich aplikacii
  * msg=log => zaloguje danu spravu do konzoly
  * msg=info => do konzoly zaloguje ziskane informacie o aplikacii
  * msg=applications => zoznam podla filter=[running|all], type=[frontend|backend], posle na response_topic=(nazov_topicu). odpoved bude mat tiez nastavene msg=applications
  * msg=workspaces => podla zoznamu "node_manager"-ov, posle na response_topic=(nazov_topicu)
  * msg=approbations => zatial napevno, posle na response_topic=(nazov_topicu)
* node/(hostname) - spravy pre dany uzol (spracovava node_manager)
  * TODO spustanie/vypinanie aplikacii
* app/<nazov> - ovladanie kazdej aplikacie (pozor, podla typu, nie instancie! t.j. sprava pride pre vsetky spustene instancie)
  * msg=quit => mastrovi posle "lifecycle" spravu, ze konci
  * msg=info => mastrovi posle "info" spravu o type aplikacie a topicoch, na ktore posiela/pocuva
  * msg=status => mastrovi posle "lifecycle" spravu, ze je ok
  * ostatne => mastrovi posle "log" spravu ze dostal neznamu spravu
* app/(nazov)/(node) - ovladanie konkretnej instancie, moze spracovavat ten isty kod ako app/(nazov)

Niekoľko príkladov publikovania správ:
```shell
mosquitto_sub -d -t app_controller
mosquitto_pub -t app_controller -m '{"msg": "start_backends"}'
mosquitto_pub -t app_controller -m '{"msg": "applications", "response_topic": "qwe"}'
mosquitto_pub -t app_controller -m '{"msg": "applications", "response_topic": "qwe", "filter": "running"}'
mosquitto_pub -t app_controller -m '{"msg": "applications", "response_topic": "qwe", "filter": "running", "type":"system"}'
mosquitto_pub -t app_controller -m '{"msg": "applications", "type": "app", "response_topic": "qwe"}'
mosquitto_pub -t app_controller -m '{"msg": "workspaces", "response_topic": "qwe"}'
mosquitto_pub -t app_controller -m '{"msg": "approbations", "response_topic": "qwe"}'
mosquitto_pub -t app/app_controller -m '{"msg": "info"}'
mosquitto_pub -t app/app_controller -m '{"msg": "status"}'
mosquitto_pub -t app/app_controller -m '{"msg": "quit"}'
mosquitto_pub -t app/app_controller/mvagac-X230 -m '{"msg": "quit"}'
mosquitto_pub -t node/mvagac-X230 -m '{"msg": "run", "type": "frontend", "name": "demo_hra2d_p"}'
```

## Our hardware

Aktuálny hardvér pozostáva z:
* mozaiky z 8 monitorov a RPI1
* projektora s RPI4, na ktoré je pripojené
  * kamera
  * kinect
  * mikrofón
  * teplomer
  * vlhkomer

