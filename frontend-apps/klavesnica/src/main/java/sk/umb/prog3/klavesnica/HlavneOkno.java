package sk.umb.prog3.klavesnica;

import java.awt.*;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;

import javax.swing.JPanel;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.paho.client.mqttv3.*;

/**
 * Inspirovane videom https://www.youtube.com/watch?v=9dzhgsVaiSo
 * 
 * @author mvagac
 *
 */
public class HlavneOkno extends JPanel implements WindowListener, KeyListener {

	private static final String CONST_KLAVESNICA_TOPIC = "klavesnica";

	// mqtt
	private MqttClient client;

	// json
	ObjectMapper mapper = new ObjectMapper();

	public HlavneOkno() {
		super();
		setPreferredSize(new Dimension(100, 100));
		// stlacene klavesy budu oznamene oknu
		setFocusable(true);
		requestFocus();
		addKeyListener(this);
		// priprav sa na odosielanie mqtt sprav
		try {
			client = new MqttClient("tcp://localhost:1883", "moj_klient-pub");
			client.connect();
		} catch (MqttException e) {
			e.printStackTrace();
		}
	}

	@Override
	public void windowOpened(WindowEvent e) {
	}

	@Override
	public void windowClosing(WindowEvent e) {
		try {
			client.disconnect();
			client.close();
		} catch (MqttException ex) {
			ex.printStackTrace();
		}
		System.exit(0);
	}

	@Override
	public void windowClosed(WindowEvent e) {
	}

	@Override
	public void windowIconified(WindowEvent e) {
	}

	@Override
	public void windowDeiconified(WindowEvent e) {
	}

	@Override
	public void windowActivated(WindowEvent e) {
	}

	@Override
	public void windowDeactivated(WindowEvent e) {
	}

	@Override
	public void keyTyped(KeyEvent key) {
	}

	private void posliKlavesaSprava(KeyEvent key, String stav) {
		KlavesaSprava kmsg = new KlavesaSprava();
		kmsg.setStav(stav);
		switch (key.getKeyCode()) {
			case KeyEvent.VK_LEFT:
				kmsg.setKlavesa("DOLAVA");
				break;
			case KeyEvent.VK_RIGHT:
				kmsg.setKlavesa("DOPRAVA");
				break;
			case KeyEvent.VK_UP:
				kmsg.setKlavesa("HORE");
				break;
			case KeyEvent.VK_DOWN:
				kmsg.setKlavesa("DOLE");
				break;
			default:
				kmsg.setKlavesa("" + key.getKeyChar());
		}
		try {
			String jsonStr = mapper.writeValueAsString(kmsg);
			System.out.println("posielam: " + jsonStr);
			MqttMessage message = new MqttMessage();
			message.setPayload(jsonStr.getBytes());
			client.publish(CONST_KLAVESNICA_TOPIC, message);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	@Override
	public void keyPressed(KeyEvent key) {
		posliKlavesaSprava(key, "STLACENA");
	}

	@Override
	public void keyReleased(KeyEvent key) {
		posliKlavesaSprava(key, "PUSTENA");
	}

}
