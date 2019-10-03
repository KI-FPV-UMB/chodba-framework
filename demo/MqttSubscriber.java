import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

public class MqttSubscriber implements MqttCallback {

	private MqttClient client;

	public static void main(String[] args) throws MqttException {
		new MqttSubscriber().pracuj();
	}

	public void pracuj() throws MqttException {
		client = new MqttClient("tcp://localhost:1883", "moj_klient");
		client.connect();
		client.setCallback(this);
		client.subscribe("pokus");
	}

	@Override
	public void connectionLost(Throwable cause) {
		// TODO Auto-generated method stub
	}

	@Override
	public void messageArrived(String topic, MqttMessage message) throws Exception {
		System.out.println("prijata sprava: " + message);
		if ("koniec".equalsIgnoreCase(message.toString())) {
			System.out.println("koncim...");
			client.disconnect();
			client.close();
//			System.exit(0);
		}
	}

	@Override
	public void deliveryComplete(IMqttDeliveryToken token) {
		// TODO Auto-generated method stub
	}

}

