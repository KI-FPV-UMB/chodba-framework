package sk.umb.prog3.hra2d.aktivne_prvky;

import java.util.Properties;

import sk.umb.prog3.hra2d.bludisko.Bludisko;

/**
 * Pod aktivnym prvkom sa rozumeju prisery, rozne bonusy.
 * 
 * @author mvagac
 *
 */
public class AktivnyPrvok {

	protected Bludisko bludisko;

	protected float x;
	protected float y;

	protected float frame = 0;

	protected SpravanieAktivnehoPrvku spravanie;

	protected Properties vlastnosti = new Properties();

	public AktivnyPrvok(Bludisko bludisko, float x, float y, SpravanieAktivnehoPrvku spravanie) {
		this.bludisko = bludisko;
		this.x = x;
		this.y = y;
		this.spravanie = spravanie;
	}

	public SpravanieAktivnehoPrvku getSpravanie() {
		return spravanie;
	}

	public float getX() {
		return x;
	}

	public float getY() {
		return y;
	}

	public void zmenX(float dx) {
		x += dx;
	}

	public void zmenY(float dy) {
		y += dy;
	}

	public void nastavVlastnost(String nazov, String hodnota) {
		vlastnosti.setProperty(nazov, hodnota);
	}

	public String citajVlastnost(String nazov) {
		return vlastnosti.getProperty(nazov);
	}

	public int getMaxX() {
		return bludisko.getSirka()-1;
	}

	public int getMaxY() {
		return bludisko.getVyska()-1;
	}

}
