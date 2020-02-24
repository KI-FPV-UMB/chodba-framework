package sk.umb.prog3.demohra2d.gui;

import org.json.JSONObject;
import sk.umb.prog3.demohra2d.mqtt.JPanelMqtt;
import sk.umb.prog3.demohra2d.mqtt.MqttParams;

import java.awt.Dimension;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.util.Properties;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Hlavne okno aplikacie...
 * 
 * @author mvagac
 *
 */
public class HlavneOkno extends JPanelMqtt implements KeyListener {

	static Logger logger = Logger.getLogger("sk.umb.prog3.demohra2d.gui");

	private ResourceBundle texty;

	public HlavneOkno(ResourceBundle texty, Properties nastavenia) {
		super(nastavenia);
		logger.log(Level.FINER, "vytvaram hlavne okno");
		// nastav velkost okna
		setPreferredSize(new Dimension(300, 200));
		// stlacene klavesy budu oznamene oknu
		setFocusable(true);
		requestFocus();
		addKeyListener(this);
	}

	@Override
	public void keyPressed(int keyCode) {
	}

	@Override
	public void keyReleased(int keyCode) {
	}

	@Override
	public void keyTyped(KeyEvent key) {
	}

	@Override
	public void keyPressed(KeyEvent key) {
	}

	@Override
	public void keyReleased(KeyEvent key) {
	}

}
