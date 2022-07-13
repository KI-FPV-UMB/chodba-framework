package sk.umb.prog3.hra2d.mqtt;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Properties;
import java.util.UUID;

public class MqttParams {

    public static final String ID = "id";
    public static final String NAME = "name";
    public static final String TYPE = "type";
    public static final String NODE = "node";
    public static final String MQTT_BROKER_HOST = "mqtt_broker_host";
    public static final String MQTT_BROKER_PORT = "mqtt_broker_port";
    public static final String SCREEN_WIDTH = "screen_width";
    public static final String SCREEN_HEIGHT = "screen_height";
    public static final String USER_TOPIC = "user_topic";
    public static final String NICKNAME = "nickname";
    public static final String APPROBATION = "approbation";

    public static void init(String[] args, Properties nastavenia) throws UnknownHostException {
        nastavenia.setProperty(ID, UUID.randomUUID().toString());
        nastavenia.setProperty(NODE, InetAddress.getLocalHost().getHostName());
        if (args.length > 0) {
            nastavenia.setProperty(MQTT_BROKER_HOST, args[0]);
        }
        if (args.length > 1) {
            nastavenia.setProperty(MQTT_BROKER_PORT, args[1]);
        }
        if (args.length > 2 && !"-".equals(args[2])) {
            nastavenia.setProperty(SCREEN_WIDTH, args[2]);
        }
        if (args.length > 3 && !"-".equals(args[3])) {
            nastavenia.setProperty(SCREEN_HEIGHT, args[3]);
        }
        if (args.length > 4) {
            nastavenia.setProperty(USER_TOPIC, args[4]);
        }
        if (args.length > 5) {
            nastavenia.setProperty(NICKNAME, args[5]);
        }
        if (args.length > 6) {
            nastavenia.setProperty(APPROBATION, args[6]);
        }
    }

}
