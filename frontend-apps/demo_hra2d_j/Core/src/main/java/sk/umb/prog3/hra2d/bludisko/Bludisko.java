package sk.umb.prog3.hra2d.bludisko;

import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.ScriptException;

import sk.umb.prog3.hra2d.aktivne_prvky.AktivnyPrvok;
import sk.umb.prog3.hra2d.aktivne_prvky.Hrac;
import sk.umb.prog3.hra2d.aktivne_prvky.SpravanieAktivnehoPrvku;

/**
 * 
 * @author mvagac
 *
 */
public class Bludisko {

	protected int[][] bludisko;
	protected List<Dlazdica> dlazdice = new ArrayList<Dlazdica>();
	protected int sirka;
	protected int vyska;
	protected int dlazdicaSirka;
	protected int dlazdicaVyska;
	protected List<AktivnyPrvok> aktivnePrvky = new ArrayList<AktivnyPrvok>();
	protected Hrac hrac;
	protected String obrazky;

	public Bludisko(String obrazky, String uroven) throws IOException, ScriptException {
		this.obrazky = obrazky;
		nacitajBludisko(obrazky, uroven);
		nacitajAktivnePrvky(obrazky, uroven);
	}

	private void nacitajBludisko(String obrazky, String uroven) throws IOException {
		Scanner s = null;
		try {
			// nacitaj subor "bludisko.dat" z daneho adresara (urovne) z classpath
			URL url = ClassLoader.getSystemResource(uroven + "bludisko.dat");
			s = new Scanner(url.openStream());
			// nacitaj prve dve cele cisla - sirku a vysku
			sirka = s.nextInt();
			vyska = s.nextInt();
			bludisko = new int[sirka][vyska];
			// nacitaj bludisko zo suboru
			for (int j = 0; j < vyska; j++) {
				for (int i = 0; i < sirka; i++) {
					bludisko[i][j] = s.nextInt();
				}
			}
			// nacitaj sirku/vysku dlazdic
			dlazdicaSirka = s.nextInt();
			dlazdicaVyska = s.nextInt();
			// nacitaj definicie (grafiku) dlazdic
			while (s.hasNext()) {
				boolean priechodna = s.nextBoolean();
				String nazovSuboru = s.next();
				Dlazdica d = novaDlazdica(priechodna, obrazky + nazovSuboru);
				dlazdice.add(d);
			}
		} finally {
			if (s != null) {
				s.close();
			}
		}
	}

	protected Dlazdica novaDlazdica(boolean priechodna, String nazovSuboru) throws IOException {
		return new Dlazdica(priechodna);
	}

	public int getSirka() {
		return sirka;
	}

	public int getVyska() {
		return vyska;
	}

	public int getDlazdicaSirka() {
		return dlazdicaSirka;
	}

	public int getDlazdicaVyska() {
		return dlazdicaVyska;
	}

	private void nacitajAktivnePrvky(String obrazky, String uroven) throws IOException, ScriptException {
		// priprav prostredie na spustanie skriptov
		ScriptEngineManager manager = new ScriptEngineManager();
		ScriptEngine engine = manager.getEngineByName("js");
		if (System.getProperty("java.version").startsWith("1.8.") || System.getProperty("java.version").startsWith("11.")) {
			engine.eval("load(\"nashorn:mozilla_compat.js\");");
		}
		// spristupni instanciu bludiska v skripte
		engine.put("bludisko", this);
		// nacitaj skript zo suboru a spusti ho
		URL url = ClassLoader.getSystemResource(uroven + "aktivne_prvky.js");
		engine.eval(new InputStreamReader(url.openStream()));
	}

	public void nastavHraca(int x, int y, float deltaPohyb, float deltaAnimacia, String nazovSuboru) throws IOException {
		hrac = new Hrac(this, x, y, deltaPohyb, deltaAnimacia);
	}

	public void pridajAktivnyPrvok(int x, int y, String nazovSuboru, SpravanieAktivnehoPrvku spravanie) throws IOException {
		AktivnyPrvok ap = new AktivnyPrvok(this, x, y, spravanie);
		ap.getSpravanie().inicializuj(ap);
		aktivnePrvky.add(ap);
	}

	public void uprav() {
		for (AktivnyPrvok ap : aktivnePrvky) {
			ap.getSpravanie().uprav();
		}
		hrac.uprav();
	}

	/**
	 * Zisti, ci sa da ist na dane suradnice.
	 * 
	 * @param x
	 * @param y
	 * @return
	 */
	public boolean mozeIst(float x, float y) {
		if (x<0 || x>getSirka()-1 || y<0 || y>getVyska()-1) return false;
		if (!dlazdice.get(bludisko[(int)x][(int)y]).priechodna) return false;
		if (!dlazdice.get(bludisko[(int)(x+0.9)][(int)y]).priechodna) return false;
		if (!dlazdice.get(bludisko[(int)x][(int)(y+0.9)]).priechodna) return false;
		if (!dlazdice.get(bludisko[(int)(x+0.9)][(int)(y+0.9)]).priechodna) return false;
		return true;
	}

	/**
	 * Zisti koliziu s aktivnym prvkom.
	 * 
	 * @param h
	 * @return
	 */
	public AktivnyPrvok kolizia(Hrac h) {
		for (AktivnyPrvok ap : aktivnePrvky) {
			if (h.getX()+1<ap.getX()) continue;
			if (h.getY()+1<ap.getY()) continue;
			if (ap.getX()+1<h.getX()) continue;
			if (ap.getY()+1<h.getY()) continue;
			ap.getSpravanie().kolizia(h);
			return ap;
		}
		return null;
	}

}
