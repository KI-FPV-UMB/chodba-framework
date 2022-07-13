package sk.umb.prog3.hra2d.aktivne_prvky;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

import sk.umb.prog3.hra2d.bludisko.BludiskoGrafika;

/**
 * 
 * @author mvagac
 *
 */
public class AktivnyPrvokGrafika extends AktivnyPrvok {

	private BufferedImage obrazok;

	public AktivnyPrvokGrafika(BludiskoGrafika bludisko, int x, int y, String nazovSuboru, SpravanieAktivnehoPrvku spravanie) throws IOException {
		super(bludisko, x, y, spravanie);
		obrazok = ImageIO.read(getClass().getResourceAsStream(nazovSuboru));
	}

	public void kresli(Graphics g) {
		g.drawImage(obrazok, (int)(x*bludisko.getDlazdicaSirka()), (int)(y*bludisko.getDlazdicaVyska()), null);
/*		// na bonuse sa bude animovat maly obdlznik - priklad jeho animacie
		g.setColor(Color.RED);
		g.drawRect((int)(x*bludisko.getDlazdicaSirka()) + stav, (int)(y*bludisko.getDlazdicaVyska()), 10, 10); TODO */
	}

}
