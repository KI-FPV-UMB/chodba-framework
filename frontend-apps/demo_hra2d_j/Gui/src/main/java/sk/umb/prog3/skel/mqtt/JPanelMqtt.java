package sk.umb.prog3.demohra2d.mqtt;

import org.eclipse.paho.client.mqttv3.*;
import org.json.JSONArray;
import org.json.JSONObject;

import javax.swing.*;
import java.awt.event.KeyEvent;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Implementacia Swing okna pomocou triedy JPanel, rozsirena o spracovanie Mqtt sprav. Pri vytvarani instancie
 * sa pripoji k Mqtt brokeru a prihlasi sa na odoberanie sprav na predefinovanom kanali. Okrem toho zverejnuje
 * spravy o zivotnom cykle aplikacie.
 *
 * @author mvagac
 */
public class JPanelMqtt extends JPanel implements MqttCallback {

    static Logger logger = Logger.getLogger("sk.umb.prog3.demohra2d.mqtt");

    private static final String KEY_DOLAVA_NAME = "dolava";
    private static final int KEY_DOLAVA_CODE = KeyEvent.VK_LEFT;
    private static final String KEY_DOPRAVA_NAME = "doprava";
    private static final int KEY_DOPRAVA_CODE = KeyEvent.VK_RIGHT;
    private static final String KEY_HORE_NAME = "hore";
    private static final int KEY_HORE_CODE = KeyEvent.VK_UP;
    private static final String KEY_DOLE_NAME = "dole";
    private static final int KEY_DOLE_CODE = KeyEvent.VK_DOWN;

    protected Properties nastavenia;
    private MqttClient client;

    // jedinecna cesta/topic k aktualnej instancii tejto aplikacie
    private String getSrc() {
        return "node/" + nastavenia.getProperty(MqttParams.NODE) + "/" + nastavenia.getProperty(MqttParams.NAME);
    }

    /**
     * Vytvor instanciu JPanelu rozsirenu o Mqtt volania. Pripoj sa k Mqtt brokeru, posielaj spravy o zivotnom cykle,
     * prihlas sa na odoberanie sprav urcenych pre nasu aplikaciu. Nastav hook pre pripad ukoncenia aplikacie - v takom
     * pripade to oznam ako zmenu lifecycle-u a korektne ukonci pripojenie na Mqtt broker.
     *
     * @param nastavenia
     */
    public JPanelMqtt(Properties nastavenia) {
        this.nastavenia = nastavenia;
        // ak je nakonfigurovany mqtt broker, sprav spojenie
        if (nastavenia.getProperty(MqttParams.MQTT_BROKER_HOST) != null
                && nastavenia.getProperty(MqttParams.MQTT_BROKER_PORT) != null) {
            try {
                // pripojenie k mqtt brokeru
                String brokerUri = "tcp://" + nastavenia.getProperty(MqttParams.MQTT_BROKER_HOST)
                                    + ":" + nastavenia.getProperty(MqttParams.MQTT_BROKER_PORT);
                logger.info("pripajam sa k mqtt brokeru " + brokerUri);
                client = new MqttClient(brokerUri, nastavenia.getProperty(MqttParams.ID));
                MqttConnectOptions opt = new MqttConnectOptions();
//                opt.setMqttVersion(4);
                opt.setCleanSession(false);
//                opt.setKeepAliveInterval(30);
                opt.setAutomaticReconnect(true);
                client.setCallback(this);
                client.connect(opt);
                logger.info("hotovo");
                publishLifecycleMessage("starting");
                // sleduj mqtt spravy
                client.subscribe("app/" + nastavenia.getProperty(MqttParams.NAME));
                client.subscribe(getSrc());
                // zverejni ovladanie
                publishControlLayoutMessage();
                // aplikacia spustena
                publishLifecycleMessage("running");
            } catch (MqttException e) {
                logger.severe("chyba mqtt");
                StringWriter sw = new StringWriter();
                PrintWriter pw = new PrintWriter(sw);
                e.printStackTrace(pw);
                logger.severe(pw.toString());
            }
            Runtime.getRuntime().addShutdownHook(new Thread() {
                public void run() {
                    stopApp();
                }
            });
        }
    }

    /**
     * Zverejni standardne ovladanie pomocou sipok. Ak to nebude aplikacii vyhovovat, moze tuto metodu prekryt vlastnou.
     */
    protected void publishControlLayoutMessage() {
        if (nastavenia.getProperty(MqttParams.USER_TOPIC) != null) {
            Map msg = new HashMap();
            msg.put("grid_width", "6");
            msg.put("grid_height", "4");
            msg.put("type", "static");
            // klavesy
            JSONArray ja = new JSONArray();
            // dolava
            JSONObject jodolava = new JSONObject();
            jodolava.put("name", KEY_DOLAVA_NAME);
            jodolava.put("x", "0");
            jodolava.put("y", "1");
            jodolava.put("w", "2");
            jodolava.put("h", "2");
            jodolava.put("title", "<-");
            jodolava.put("type", "button");
            ja.put(jodolava);
            // doprava
            JSONObject jodoprava = new JSONObject();
            jodoprava.put("name", KEY_DOPRAVA_NAME);
            jodoprava.put("x", "4");
            jodoprava.put("y", "1");
            jodoprava.put("w", "2");
            jodoprava.put("h", "2");
            jodoprava.put("title", "->");
            jodoprava.put("type", "button");
            ja.put(jodoprava);
            // hore
            JSONObject johore = new JSONObject();
            johore.put("name", KEY_HORE_NAME);
            johore.put("x", "2");
            johore.put("y", "0");
            johore.put("w", "2");
            johore.put("h", "2");
            johore.put("title", "^");
            johore.put("type", "button");
            ja.put(johore);
            // dole
            JSONObject jodole = new JSONObject();
            jodole.put("name", KEY_DOLE_NAME);
            jodole.put("x", "2");
            jodole.put("y", "2");
            jodole.put("w", "2");
            jodole.put("h", "2");
            jodole.put("title", "v");
            jodole.put("type", "button");
            ja.put(jodole);
            // nastav cele ovladanie
            msg.put("control_elements", ja);
            publishMessage("control_layout", msg, nastavenia.getProperty(MqttParams.USER_TOPIC));
        }
    }

    /**
     * Odosli spravu opisujucu zivotny cyklus aplikacie.
     *
     * @param status
     */
    protected final void publishLifecycleMessage(String status) {
        Map msg = new HashMap();
        msg.put("id", nastavenia.getProperty(MqttParams.ID));
        msg.put("name", nastavenia.getProperty(MqttParams.NAME));
        msg.put("type", nastavenia.getProperty(MqttParams.TYPE));
        msg.put("node", nastavenia.getProperty(MqttParams.NODE));
//        msg.put("runon", );
//        msg.put("enabled", );
//        msg.put("labels", );
        msg.put("user_topic", nastavenia.getProperty(MqttParams.USER_TOPIC));
        msg.put("nickname", nastavenia.getProperty(MqttParams.NICKNAME));
        msg.put("approbation", nastavenia.getProperty(MqttParams.APPROBATION));
        msg.put("status", status);
        publishMessage("lifecycle", msg, "master");
    }

    /**
     * Metoda sluzi na odoslanie vseobecnej Mqtt spravy (vo formate json). Vsetky "nase" spravy su vo formate json
     * a maju atribut "msg", ktory definuje typ spravy. Okrem toho kazda sprava obsahuje sadu standardnych atributov
     * (timestamp, src, name). K tym su pridane specificke atributy, ktore su definovane v mape msgBody.
     *
     * @param msgHead
     * @param msgBody
     * @param topic
     */
    protected final void publishMessage(String msgHead, Map msgBody, String topic) {
        if (client == null)
            return;
        try {
            // dopln spravu o povinne atributy
            msgBody.put("msg", msgHead);
            msgBody.put("timestamp", new SimpleDateFormat("yyyyMMddHHmmss").format(new Date()));
            msgBody.put("src", getSrc());
            msgBody.put("name", nastavenia.getProperty(MqttParams.NAME));
            // publikovanie spravy
            MqttMessage message = new MqttMessage();
            message.setPayload(new JSONObject(msgBody).toString().getBytes());
            client.publish(topic, message);
        } catch (MqttException e) {
            logger.severe("chyba mqtt");
            StringWriter sw = new StringWriter();
            PrintWriter pw = new PrintWriter(sw);
            e.printStackTrace(pw);
            logger.severe(pw.toString());
        }
    }

    /**
     * Strata spojenia na Mqtt broker.
     *
     * @param cause
     */
    @Override
    public void connectionLost(Throwable cause) {
        logger.severe("mqtt rozpadnute spojenie");
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        cause.printStackTrace(pw);
        logger.severe(pw.toString());
    }

    /**
     * Metoda zavolana pri prijati Mqtt spravy. Osetry standardne typy sprav, nestandardne deleguje na metodu onMsg,
     * ktora by mala byt prekryta v potomkovi.
     *
     * @param topic
     * @param message
     * @throws Exception
     */
    @Override
    public void messageArrived(String topic, MqttMessage message) throws Exception {
        logger.finer("prijata sprava: " + message);
        JSONObject msgJson = new JSONObject(message.toString());
        if (msgJson.isNull("msg")) {
            Map log = new HashMap();
            log.put("log", "neznamy typ spravy: " + message.toString());
            publishMessage("log", log, "master");
            return;
        }
        String msg = msgJson.getString("msg");
        if ("quit".equals(msg)) {
            logger.info("poziadavka na ukoncenie aplikacie");
            super.setVisible(false);
            stopApp();
            System.exit(0);
        } else if ("info".equals(msg)) {
            Map info = new HashMap();
            info.put("id", nastavenia.getProperty(MqttParams.ID));
            info.put("name", nastavenia.getProperty(MqttParams.NAME));
            publishMessage("info", info, "master");
        } else if ("status".equals(msg)) {
            publishLifecycleMessage("running");
        } else {
            try {
                onMsg(msgJson);
            } catch (Exception e) {
                logger.severe("chyba pri spracovanie spravy: " + message.toString());
                StringWriter sw = new StringWriter();
                PrintWriter pw = new PrintWriter(sw);
                e.printStackTrace(pw);
                logger.severe(pw.toString());
                // posli info o chybe aj mastrovi
                Map log = new HashMap();
                log.put("log", "chyba pri spracovani spravy: " + message.toString());
                publishMessage("log", log, "master");
            }
        }
    }

    /**
     * Metoda by mala byt prekryta v potomkovi. Ak nie je a zavola sa, znamena to ze prisiel specificky typ spravy,
     * ktory neviem spracovat vseobecne a mal by byt spracovany v potomkovi. Preto to zaloguj ako neznamy typ spravy.
     *
     * @param msgJson
     */
    public void onMsg(JSONObject msgJson) {
        String msg = msgJson.getString("msg");
        if ("control_action".equals(msg)) {
            String name = msgJson.getString("name");
            String type = msgJson.getString("type");
            logger.finer("klavesa " + name + ": " + type);
            // podla nazvu stlacenej klavesy vyber kod
            int code = -1;
            if (KEY_DOLAVA_NAME.equals(name)) {
                code = KEY_DOLAVA_CODE;
            }
            if (KEY_DOPRAVA_NAME.equals(name)) {
                code = KEY_DOPRAVA_CODE;
            }
            if (KEY_HORE_NAME.equals(name)) {
                code = KEY_HORE_CODE;
            }
            if (KEY_DOLE_NAME.equals(name)) {
                code = KEY_DOLE_CODE;
            }
            // podla druhu udalosti zavolaj stlacena/pustena
            if ("keydown".equals(type)) {
                keyPressed(code);
            }
            if ("keyup".equals(type)) {
                keyReleased(code);
            }
        } else {
            Map log = new HashMap();
            log.put("log", "neznamy typ spravy: " + msgJson.toString());
            publishMessage("log", log, "master");
        }
    }

    public void keyPressed(int keyCode) {
    }

    public void keyReleased(int keyCode) {
    }

    @Override
    public void deliveryComplete(IMqttDeliveryToken token) {
    }

    private void stopApp() {
        logger.log(Level.INFO, "posielam spravu o konceni");
        publishLifecycleMessage("quitting");
        try {
            if (client != null) {
                logger.log(Level.INFO, "odpajam MQTT klienta");
                client.disconnect();
                client.close();
                client = null;
            }
        } catch (MqttException e) {
            logger.severe("chyba mqtt");
            StringWriter sw = new StringWriter();
            PrintWriter pw = new PrintWriter(sw);
            e.printStackTrace(pw);
            logger.severe(pw.toString());
        }
        logger.log(Level.INFO, "koncim na uzle " + nastavenia.getProperty(MqttParams.NODE));
    }

}
