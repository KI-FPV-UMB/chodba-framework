package sk.umb.prog3.hra2d;

import sk.umb.prog3.hra2d.gui.HlavneOkno;
import sk.umb.prog3.hra2d.mqtt.MqttParams;

import javax.swing.JFrame;
import java.io.IOException;
import java.net.URL;
import java.util.Locale;
import java.util.Properties;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Pociatocny bod pre spustenie Gui aplikacie. Vytvori sa instancia grafickeho okna.
 * 
 * @author mvagac
 *
 */
public class HlavnaSwing {

	static Logger logger = Logger.getLogger("sk.umb.prog3.demohra2d");

	public static void main(String[] args) throws IOException {
		logger.log(Level.INFO, "spustam aplikaciu");
		// priprav nastavenia
		Properties nastavenia = new Properties();
		URL url = ClassLoader.getSystemResource("nastavenia.properties");
		nastavenia.load(url.openStream());
		MqttParams.init(args, nastavenia);
		logger.info("nastavenia: " + nastavenia);
		// priprav lokalizaciu
		Locale l = new Locale("sk");
		ResourceBundle texty = ResourceBundle.getBundle("texty", l);
		// vytvor a zobraz okno
		javax.swing.SwingUtilities.invokeLater(new Runnable(){
			public void run() {
				vytvorAZobrazHlavneOkno(texty, nastavenia);
			}
		});
	}

	private static void vytvorAZobrazHlavneOkno(ResourceBundle texty, Properties nastavenia) {
		JFrame window = new JFrame(texty.getString("hlavneokno.titulok"));
		window.setContentPane(new HlavneOkno(texty, nastavenia));
		window.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		window.setResizable(false);
		window.pack();
		window.setVisible(true);
	}

}
