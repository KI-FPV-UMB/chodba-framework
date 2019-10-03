import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

public class MqttPublisher {

	public static void main(String[] args) throws MqttException {
		// pripojenie k brokeru
		MqttClient client = new MqttClient("tcp://localhost:1883", "moj_klient");
		client.connect();
		// publikovanie do kanala 'pokus'
		MqttMessage message = new MqttMessage();
		message.setPayload("Hura Java!".getBytes());
		client.publish("pokus", message);
		// odpojenie od brokera
		client.disconnect();
		client.close();
	}

}

