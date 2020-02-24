package sk.umb.prog3.hra2d.gui;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.image.BufferedImage;
import java.io.File;
import java.util.Properties;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.swing.JPanel;

import sk.umb.prog3.hra2d.bludisko.BludiskoGrafika;
import sk.umb.prog3.hra2d.mqtt.JPanelMqtt;

/**
 * Inspirovane videom https://www.youtube.com/watch?v=9dzhgsVaiSo
 * 
 * @author mvagac
 *
 */
public class HlavneOkno extends JPanelMqtt implements Runnable, KeyListener {

	static Logger logger = Logger.getLogger("sk.umb.prog3.hra2d.gui");

	private ResourceBundle texty;

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

	public HlavneOkno(ResourceBundle texty, Properties nastavenia) {
		super(nastavenia);
		logger.log(Level.FINER, "vytvaram hlavne okno");
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

}
