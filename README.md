# chodba-framework

Aktuálny hardvér pozostáva z:
* mozaiky z 8 monitorov a RPI1
* projektora s RPI4, na ktoré je pripojené
  * kamera
  * kinect
  * mikrofón
  * teplomer
  * vlhkomer

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
mosquitto_sub -d -t master
mosquitto_pub -t master -m '{"msg": "run_backends"}'
mosquitto_pub -t master -m '{"msg": "applications", "response_topic": "qwe"}'
mosquitto_pub -t master -m '{"msg": "applications", "response_topic": "qwe", "filter": "running"}'
mosquitto_pub -t master -m '{"msg": "applications", "response_topic": "qwe", "filter": "running", "type":"system"}'
mosquitto_pub -t master -m '{"msg": "applications", "type": "app", "response_topic": "qwe"}'
mosquitto_pub -t master -m '{"msg": "workspaces", "response_topic": "qwe"}'
mosquitto_pub -t master -m '{"msg": "approbations", "response_topic": "qwe"}'
mosquitto_pub -t app/master -m '{"msg": "info"}'
mosquitto_pub -t app/master -m '{"msg": "status"}'
mosquitto_pub -t app/master -m '{"msg": "quit"}'
mosquitto_pub -t app/master/mvagac-X230 -m '{"msg": "quit"}'
mosquitto_pub -t node/mvagac-X230 -m '{"msg": "run", "type": "frontend", "name": "demo_hra2d_p"}'
```

