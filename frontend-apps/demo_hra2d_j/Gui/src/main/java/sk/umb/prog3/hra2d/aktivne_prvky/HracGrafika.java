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
public class HracGrafika extends Hrac {

	private BufferedImage obrazok;

	public HracGrafika(BludiskoGrafika bludisko, int x, int y, float deltaPohyb, float deltaAnimacia, String nazovSuboru) throws IOException {
		super(bludisko, x, y, deltaPohyb, deltaAnimacia);
		obrazok = ImageIO.read(getClass().getResourceAsStream(nazovSuboru));
	}

	public void kresli(Graphics g) {
		int dx1 = (int)(x*bludisko.getDlazdicaSirka());
		int dy1 = (int)(y*bludisko.getDlazdicaVyska());
		int dx2 = dx1 + bludisko.getDlazdicaSirka();
		int dy2 = dy1 + bludisko.getDlazdicaVyska();
		int sx1 = ((int)frame)*bludisko.getDlazdicaSirka();
		int sy1 = 0;
		int sx2 = sx1 + bludisko.getDlazdicaSirka();
		int sy2 = sy1 + bludisko.getDlazdicaVyska();
		g.drawImage(obrazok, dx1, dy1, dx2, dy2, sx1, sy1, sx2, sy2, null);
	}

}
