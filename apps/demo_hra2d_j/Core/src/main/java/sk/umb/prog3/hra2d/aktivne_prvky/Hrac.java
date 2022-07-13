package sk.umb.prog3.hra2d.aktivne_prvky;

import java.io.IOException;

import sk.umb.prog3.hra2d.bludisko.Bludisko;

/**
 * 
 * @author mvagac
 *
 */
public class Hrac extends AktivnyPrvok {

	private boolean dolava = false;
	private boolean doprava = false;
	private boolean hore = false;
	private boolean dole = false;

	private float deltaPohyb;
	private float deltaAnimacia;

	public Hrac(Bludisko bludisko, float x, float y, float deltaPohyb, float deltaAnimacia) throws IOException {
		super(bludisko, x, y, null);
		this.deltaPohyb = deltaPohyb;
		this.deltaAnimacia = deltaAnimacia;
	}

	public void uprav() {
		// animacia
		if (dolava || doprava || hore || dole) {
			frame += deltaAnimacia;
			if (frame>=3) {
				frame = 0;
			}
		}
		// kolizie steny
		if (dolava) {
			if (bludisko.mozeIst(x-deltaPohyb, y)) {
				x -= deltaPohyb;
			} else {
				if (x-deltaPohyb<0) {
					x = ((int)(x-deltaPohyb));
				} else {
					x = ((int)(x-deltaPohyb))+1;
				}
			}
		}
		if (doprava) {
			if (bludisko.mozeIst(x+deltaPohyb, y)) {
				x += deltaPohyb;
			} else {
				x = ((int)(x+deltaPohyb));
			}
		}
		if (hore) {
			if (bludisko.mozeIst(x, y-deltaPohyb)) {
				y -= deltaPohyb;
			} else {
				if (y-deltaPohyb<0) {
					y = ((int)(y-deltaPohyb));
				} else {
					y = ((int)(y-deltaPohyb))+1;
				}
			}
		}
		if (dole) {
			if (bludisko.mozeIst(x, y+deltaPohyb)) {
				y += deltaPohyb;
			} else {
				y = ((int)(y+deltaPohyb));
			}
		}
		// kolizie aktivne prvky
		AktivnyPrvok ap = bludisko.kolizia(this);
		if (ap!=null) {
			System.out.println("mam ho: " + ap);
		}
	}

	public void setDolava(boolean dolava) {
		this.dolava = dolava;
	}

	public void setDoprava(boolean doprava) {
		this.doprava = doprava;
	}

	public void setHore(boolean hore) {
		this.hore = hore;
	}

	public void setDole(boolean dole) {
		this.dole = dole;
	}

	public int getMaxX() {
		return bludisko.getSirka()-1;
	}

	public int getMaxY() {
		return bludisko.getVyska()-1;
	}

}
