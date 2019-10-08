package sk.umb.prog3.hra2d.gui;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.awt.image.BufferedImage;
import java.io.File;

import javax.swing.JPanel;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.paho.client.mqttv3.*;
import sk.umb.prog3.hra2d.bludisko.BludiskoGrafika;

/**
 * Inspirovane videom https://www.youtube.com/watch?v=9dzhgsVaiSo
 * 
 * @author mvagac
 *
 */
public class HlavneOkno extends JPanel implements WindowListener, Runnable, KeyListener, MqttCallback {

	private static final String CONST_KLAVESNICA_TOPIC = "klavesnica";

	// rozmery okna
	private static final int CONST_ZVACSENIE = 2;

	// beh hry
	private Thread vlakno;
	private boolean hrame = true;
	private int FPS = 60;
	private long casPreFPS = 1000 / FPS;

	// grafika
	private static final String CONST_OBRAZKY = "/obrazky/";		// adresar s obrazkami
	private BufferedImage doubleBuffer;

	// bludisko
	private BludiskoGrafika bludisko;

	// mqtt
	private MqttClient client;

	// json
	ObjectMapper mapper = new ObjectMapper();

	public HlavneOkno() {
		super();
		// vytvor bludisko
		try {
			bludisko = new BludiskoGrafika(CONST_OBRAZKY, "u1/");	// TODO uroven1
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		// nastav velkost okna
		setPreferredSize(new Dimension(bludisko.getSirka()*bludisko.getDlazdicaSirka()*CONST_ZVACSENIE, bludisko.getVyska()*bludisko.getDlazdicaVyska()*CONST_ZVACSENIE));
		// stlacene klavesy budu oznamene oknu
		setFocusable(true);
		requestFocus();
		addKeyListener(this);
		// koli animaciam sa bude stale vykonavat druhe vlakno
		vlakno = new Thread(this);
		vlakno.start();
		// prijimaj mqtt spravy
		try {
			client = new MqttClient("tcp://localhost:1883", "moj_klient-sub");
			client.connect();
			client.setCallback(this);
			client.subscribe(CONST_KLAVESNICA_TOPIC);
		} catch (MqttException e) {
			e.printStackTrace();
		}
	}

	public void run() {
		// inicializuj premenne
		doubleBuffer = new BufferedImage(bludisko.getSirka()*bludisko.getDlazdicaSirka(), bludisko.getVyska()*bludisko.getDlazdicaVyska(), BufferedImage.TYPE_INT_RGB);
		while(hrame) {
			long start = System.nanoTime();
			// vykonaj potrebne zmeny objektov
			bludisko.uprav();
			// premaz grafiku
			doubleBuffer.getGraphics().setColor(Color.WHITE);
			doubleBuffer.getGraphics().fillRect(0, 0, bludisko.getSirka()*bludisko.getDlazdicaSirka(), bludisko.getVyska()*bludisko.getDlazdicaVyska());
			// vykresli objekty
			bludisko.kresli(doubleBuffer.getGraphics());
			// skopiruj double buffer na obrazovku
			zobrazObsahDoubleBuffera();
			// pockaj cas potrebny na to, aby sme docielili definovane FPS
			long elapsed = System.nanoTime() - start;
			long wait = casPreFPS - elapsed / 1000000;
			if(wait < 0) wait = 5;
			try {
				Thread.sleep(wait);
			} catch(Exception e) {
				break;
			}
		}
	}

	private void zobrazObsahDoubleBuffera() {
		// vykresli double buffer do aktualneho okna (this.getGraphics())
		Graphics g2 = getGraphics();
		if (g2!=null) {
			g2.drawImage(doubleBuffer, 0, 0, bludisko.getSirka()*bludisko.getDlazdicaSirka()*CONST_ZVACSENIE, bludisko.getVyska()*bludisko.getDlazdicaVyska()*CONST_ZVACSENIE, null);
			g2.dispose();
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

	@Override
	public void keyPressed(KeyEvent key) {
		bludisko.klavesaStlacena(key.getKeyCode());
	}

	@Override
	public void keyReleased(KeyEvent key) {
		bludisko.klavesaPustena(key.getKeyCode());
	}

	@Override
	public void connectionLost(Throwable throwable) {
	}

	private int keyMsg2Awt(String msgkey) {
		if ("DOLAVA".equals(msgkey)) {
			return KeyEvent.VK_LEFT;
		}
		if ("DOPRAVA".equals(msgkey)) {
			return KeyEvent.VK_RIGHT;
		}
		if ("HORE".equals(msgkey)) {
			return KeyEvent.VK_UP;
		}
		if ("DOLE".equals(msgkey)) {
			return KeyEvent.VK_DOWN;
		}
		return -1;
	}

	@Override
	public void messageArrived(String s, MqttMessage mqttMessage) throws Exception {
		String jsonStr = mqttMessage.toString();
		System.out.println(jsonStr);
		KlavesaSprava result = mapper.readValue(jsonStr, KlavesaSprava.class);
		int key = keyMsg2Awt(result.getKlavesa());
		if (key != -1) {
			if ("STLACENA".equals(result.getStav())) {
				bludisko.klavesaStlacena(key);
			}
			if ("PUSTENA".equals(result.getStav())) {
				bludisko.klavesaPustena(key);
			}
		}
	}

	@Override
	public void deliveryComplete(IMqttDeliveryToken iMqttDeliveryToken) {
	}

}