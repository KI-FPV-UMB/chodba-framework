package sk.umb.prog3.hra2d.bludisko;

import java.awt.Graphics;
import java.awt.event.KeyEvent;
import java.io.IOException;

import javax.script.ScriptException;

import sk.umb.prog3.hra2d.aktivne_prvky.AktivnyPrvok;
import sk.umb.prog3.hra2d.aktivne_prvky.AktivnyPrvokGrafika;
import sk.umb.prog3.hra2d.aktivne_prvky.HracGrafika;
import sk.umb.prog3.hra2d.aktivne_prvky.SpravanieAktivnehoPrvku;
import sk.umb.prog3.hra2d.bludisko.Bludisko;

/**
 * 
 * @author mvagac
 *
 */
public class BludiskoGrafika extends Bludisko {

	public BludiskoGrafika(String obrazky, String uroven) throws IOException, ScriptException {
		super(obrazky, uroven);
	}

	@Override
	protected Dlazdica novaDlazdica(boolean priechodna, String nazovSuboru) throws IOException {
		return new DlazdicaGrafika(priechodna, nazovSuboru);
	}

	@Override
	public void nastavHraca(int x, int y, float deltaPohyb, float deltaAnimacia, String nazovSuboru) throws IOException {
		hrac = new HracGrafika(this, x, y, deltaPohyb, deltaAnimacia, obrazky + nazovSuboru);
	}

	@Override
	public void pridajAktivnyPrvok(int x, int y, String nazovSuboru, SpravanieAktivnehoPrvku spravanie) throws IOException {
		AktivnyPrvokGrafika ap = new AktivnyPrvokGrafika(this, x, y, obrazky + nazovSuboru, spravanie);
		ap.getSpravanie().inicializuj(ap);
		aktivnePrvky.add(ap);
	}

	public void kresli(Graphics g) {
		kresliBludisko(g);
		// kresli aktivne prvky
		for (AktivnyPrvok ap : aktivnePrvky) {
			if (ap instanceof AktivnyPrvokGrafika) {
				((AktivnyPrvokGrafika)ap).kresli(g);
			}
		}
		// kresli hraca
		((HracGrafika)hrac).kresli(g);
	}

	private void kresliBludisko(Graphics g) {
		int x = 0;
		for (int i = 0; i < bludisko.length; i++) {
			int y = 0;
			for (int j = 0; j < bludisko[i].length; j++) {
				int dc = bludisko[i][j];
				if (dc>dlazdice.size()) {
					continue;
				}
				DlazdicaGrafika d = (DlazdicaGrafika)dlazdice.get(dc);
				g.drawImage(d.getObrazok(), x, y, null);
				y += dlazdicaVyska;
			}
			x += dlazdicaSirka;
		}
	}

	public void klavesaStlacena(int k) {
//		System.out.println("stlacene " + k);
		if(k == KeyEvent.VK_LEFT) hrac.setDolava(true);
		if(k == KeyEvent.VK_RIGHT) hrac.setDoprava(true);
		if(k == KeyEvent.VK_UP) hrac.setHore(true);
		if(k == KeyEvent.VK_DOWN) hrac.setDole(true);
	}

	public void klavesaPustena(int k) {
//		System.out.println("pustene " + k);
		if(k == KeyEvent.VK_LEFT) hrac.setDolava(false);
		if(k == KeyEvent.VK_RIGHT) hrac.setDoprava(false);
		if(k == KeyEvent.VK_UP) hrac.setHore(false);
		if(k == KeyEvent.VK_DOWN) hrac.setDole(false);
	}

}
